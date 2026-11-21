from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Max, F
from django.db.models.functions import Least, Greatest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from game.models import Match, MatchEvent
from datetime import timedelta 
from django.utils import timezone
from collections import Counter, defaultdict

User = get_user_model()

class PongUniverseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', 'all') #7 days /30 d/ all, readds from ?period=7d from url
        since = None
        if(period == '7d'):
            since = timezone.now() - timedelta(days=7)
        elif (period == '30d'):
            since = timezone.now() - timedelta(days=30)

        matches_qs = Match.objects.filter(
            status=Match.Status.FINISHED
        )
        if since:
            matches_qs = matches_qs.filter(ended_at__gte=since)

        p1_stats = (
            matches_qs
            .values('player1_id')
            .annotate(
                total=Count('id'),
                wins=Count('id', filter=Q(winner_id=F('player1_id'))),
            )
        )

        p2_stats  = (
            matches_qs
            .values('player2_id')
            .annotate(
                total=Count('id'),
                wins=Count('id', filter=Q(winner_id=F('player2_id'))),
            )
        )
        total_counter = Counter()
        wins_counter = Counter()

        for row in p1_stats:
            uid = row['player1_id']
            total_counter[uid] += row['total']
            wins_counter[uid] += row['wins']

        for row in p2_stats:
            uid = row['player2_id']
            total_counter[uid] += row['total']
            wins_counter[uid] += row['wins']
        
        event_stats = (
            MatchEvent.objects
            .filter(match__in=matches_qs)
            .values('player_id')
            .annotate(
                hits=Count('id', filter=Q(event_type=MatchEvent.EventType.HIT)),
                misses=Count('id', filter=Q(event_type=MatchEvent.EventType.MISS)),
            )
        )
        hits_counter = Counter()
        misses_counter = Counter()

        for row in event_stats:
            uid = row['player_id']
            hits_counter[uid] = row['hits']
            misses_counter[uid] = row['misses']

        users = (
            User.objects
            .only('id', 'nickname', 'date_joined')
            .order_by('date_joined')
        )
        result = []

        for user in users:
            total = total_counter.get(user.id, 0)
            wins = wins_counter.get(user.id, 0)
            hits = hits_counter.get(user.id, 0)
            misses = misses_counter.get(user.id, 0)

            result.append({
                'id': user.id,
                'nickname': user.nickname,
                'date_joined': user.date_joined.isoformat(),
                'total_matches': total,
                'wins': wins,
                'losses': total - wins,
                'win_rate': round(wins / total, 2) if total > 0 else 0,
                'hit_accuracy': round(hits / (hits + misses), 2) if (hits + misses) > 0 else None,
            })

        return Response(result)

class PlayerGraphView(APIView):
    """
    GET /api/analytics/player-graph/

    Returns a 2-hop ego-network graph centered on the requesting user, 
    showing player connections based on played matches. Designed to be 
    consumed directly by d3-froce simulation on the frontend.

    Query params:
        period (str, optional): time window for match filtering
            Values: '7d' | '30d' | 'all'. Default: 'all'.
            Filter is applied to Match.ended_at
    
    Response:
        {
            "nodes": [
                {
                    "id": int, 	#User PK, used as D3 node identifier
                    "nickname": str,
                    "avatar": str | null 	#media URL or null
                    "wins": int, 	#wins within selected period, against all opponents
                    "losses": int, 	#losses within selected period, against all opponents
                    "draws": int, 	#matches with winner=NULL, against all opponents
                    "degree": int, 	#unique opponents in this graph
                    "is_current": bool 	#true only for request.user
                }, 
                ...
            ],

            "edges": [
                {
                    "source": int, 	#node id, always source < target
                    "target": int, 	#node id(normilized pair ordering)
                    "mathces": int, 	#total matches between the pair
                    "wins_source": int, 	#wins by the 'source' user
                    "wins_target": int, 	#wins by the 'target' user
                    "draws": int, 	#matches with winner=NULL
                    "last_played_at": str, 	#ISO 8601 timestamp
                },
                ...
            ],
            "meta": {
                "period": str, 	#echoes the requested filter
                "nodes_count": int, 
                "edges_count": int,
                "generated_at": str 	#ISO 8601 timestamp(UTC)
            }
        }
    
    Mathc filtering:
        - Only matches with mode='local' AND status='finished' are counted
        - AI matches are excluded (not human connection + feature not realised)
        - Remote matches are excluded (feature not realised)

    Graph scope (2-hop ego-network):
        Node selection (3 passes):
            1. request.user 	->center
            2. All users who played againts request.user ->1st circle
            3. For each user in 1st circle: top-5 partners by match count (excludin request.user) 	->2nd circle
        Nodes = union of all three sets

        Edge selection (1pass):
            All matches where BOTH players are in the node set.
            This naturally produces:
                - center-to-1st-circle efges
                - inner edges withis 1st circle
                - 1st-to-2nd circle edges
                - inner-2nd-circle edges (bridges between branches)

            The "top-5 partners" cap keeps the graph bounded even when a 1st-circle user 
            has played against many people.
            Top-N is computed withis the same period as the rest of the graph 
            (consistency over perfomance at this stage).

    Edge normalization:
        Each unordered pair {A, B} produces one efge where source = min(A.id, B.id)
        and target = max(A.id, B.id). This prevents (A, B) and (B, A) from appearting
        as duplicate efdges when players appear on diffren sides across matches

    KNown limitations (deferred):
    - top-5 cap for 2nd circle is a hardcoded constant. 
    Future: ?depth=1|2 and ?top_n=N for confugrability
    - No pagination: entire ego-network is returned in a single response.
    For users with 100+ direct opponens, response size may degrade
    Future: ?limit=N top-N by match count
    - No caching: computed on every request. Future: Redis cache keyed by (user.id, period)
    with invalidation on Match.finish


    Permissions:
        IsAuthenticated
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', 'all') #7 days /30 d/ all, readds from ?period=7d from url
        since = None
        if(period == '7d'):
            since = timezone.now() - timedelta(days=7)
        elif (period == '30d'):
            since = timezone.now() - timedelta(days=30)

        base_matches_qs = Match.objects.filter(
            mode='local',
            status=Match.Status.FINISHED,
        )
        if since:
            base_matches_qs = base_matches_qs.filter(ended_at__gte=since)
        
        me_id = request.user.id
        my_matches = base_matches_qs.filter(
            Q(player1=request.user) | Q(player2=request.user)
        )
        first_circle_ids = set()
        for m in my_matches.values('player1_id', 'player2_id'):
            first_circle_ids.add(m['player1_id'])
            first_circle_ids.add(m['player2_id'])
        first_circle_ids.discard(me_id)

        TOP_N = 5
        second_circle_ids = set()
        partner_counts = defaultdict(Counter)
        rows = base_matches_qs.filter(
            Q(player1_id__in=first_circle_ids) | Q(player2_id__in=first_circle_ids)
        ).values_list('player1_id', 'player2_id')
        for p1, p2 in rows:
            if p1 in first_circle_ids:
                partner_counts[p1][p2] += 1
            if p2 in first_circle_ids:
                partner_counts[p2][p1] += 1

        for uid, counter in partner_counts.items():
            counter.pop(me_id, None)
            counter.pop(uid, None)
            second_circle_ids.update(pid for pid, _ in counter.most_common(TOP_N))
            
        all_node_ids = {me_id} | first_circle_ids | second_circle_ids

        edges_qs = (
            base_matches_qs
            .filter(player1_id__in=all_node_ids, player2_id__in=all_node_ids)
            .annotate(
                source = Least('player1_id', 'player2_id'),
                target = Greatest('player1_id', 'player2_id'),
            )
            .values('source', 'target')
            .annotate(
                matches=Count('id'),
                wins_source=Count('id', filter=Q(winner_id=F('source'))),
                wins_target=Count('id', filter=Q(winner_id=F('target'))),
                draws=Count('id', filter=Q(winner__isnull=True)),
                last_played_at=Max('ended_at'),
            )
        )

        edges = []
        degree_counter = Counter()

        for e in edges_qs:
            if e['source'] == e['target']:
                continue
            s, t = e['source'], e['target']

            edges.append({
                'source': s,
                'target': t,
                'matches': e['matches'],
                'wins_source': e['wins_source'],
                'wins_target': e['wins_target'],
                'draws': e['draws'],
                'last_played_at': e['last_played_at'].isoformat() if e['last_played_at'] else None,
            })
            degree_counter[s] += 1
            degree_counter[t] +=1

        #node record counts all matches, also against players outside the graph
        total_counter = Counter()
        wins_counter = Counter()
        draws_counter = Counter()

        for side in ('player1_id', 'player2_id'):
            rows = (
                base_matches_qs
                .exclude(player1_id=F('player2_id'))
                .filter(**{f'{side}__in': all_node_ids})
                .values(side)
                .annotate(
                    total=Count('id'),
                    wins=Count('id', filter=Q(winner_id=F(side))),
                    draws=Count('id', filter=Q(winner__isnull=True)),
                )
            )
            for row in rows:
                total_counter[row[side]] += row['total']
                wins_counter[row[side]] += row['wins']
                draws_counter[row[side]] += row['draws']


        users = User.objects.filter(id__in=all_node_ids).only(
            'id', 'nickname', 'avatar'
        )
        nodes = []
        for user in users:
            total = total_counter.get(user.id, 0)
            wins = wins_counter.get(user.id, 0)
            draws = draws_counter.get(user.id, 0)
            losses = total - wins - draws

            nodes.append({
                'id': user.id,
                'nickname': user.nickname,
                'avatar': user.avatar.url if getattr(user, 'avatar', None) else None,
                'wins': wins,
                'losses': losses,
                'draws': draws,
                'degree': degree_counter.get(user.id, 0),
                'is_current': user.id == me_id,
            })
        
        return Response({
            'nodes': nodes,
            'edges': edges,
            'meta': {
                'period': period,
                'nodes_count': len(nodes),
                'edges_count': len(edges),
                'generated_at': timezone.now().isoformat(),
            },
        })


