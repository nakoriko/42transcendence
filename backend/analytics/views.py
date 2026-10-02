# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    views.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/28 19:13:36 by nakoriko          #+#    #+#              #
#    Updated: 2026/10/02 15:26:06 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.contrib.auth import get_user_model
# from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Avg #object to calculate aberege reaction_time for all users
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from game.models import Match, MatchEvent
from datetime import timedelta 
from django.utils import timezone

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

        users = User.objects.all().order_by('date_joined')
        result = []

        for user in users:
            match_qs = Match.objects.filter(
                Q(player1=user) | Q(player2=user),
                status=Match.Status.FINISHED
            )
            if since:
                match_qs = match_qs.filter(ended_at__gte=since)
            total = match_qs.count()
            wins = match_qs.filter(winner=user).count()
            event_qs = MatchEvent.objects.filter(match__in=match_qs, player=user)
            hits = event_qs.filter(event_type=MatchEvent.EventType.HIT).count()
            misses = event_qs.filter(event_type=MatchEvent.EventType.MISS).count()

            avg_reaction = event_qs.filter(
                event_type=MatchEvent.EventType.HIT,
                reaction_time_ms__isnull=False
            ).aggregate(avg=Avg('reaction_time_ms'))['avg']

            result.append({
                'id': user.id,
                'nickname': user.nickname or user.email,
                'date_joined': user.date_joined.isoformat(),
                'total_matches': total,
                'wins': wins,
                'losses': total - wins,
                'win_rate': round(wins / total, 2) if total > 0 else 0,
                'avg_reaction_ms': round(avg_reaction) if avg_reaction else None,
                'hit_accuracy': round(hits / (hits + misses), 2) if (hits + misses) > 0 else None,
            })
        return Response(result)

class PlayerStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', 'all')
        since = None
        if period == '7d':
            since = timezone.now() - timedelta(days=7)
        elif period =='30d':
            since = timezone.now() - timedelta(days=30)
        
        matches = Match.objects.filter(
            Q(player1=request.user) | Q(player2=request.user),
            status=Match.Status.FINISHED
        )
        if since:
                matches = matches.filter(ended_at__gte=since)
        
        #group by days via annotate
        #by_day  - query set of days with date, total matches and wins fro every sorted day
        by_day = matches.annotate(
            day=TruncDate('ended_at')
        ).values('day').annotate(
            total=Count('id'),
            wins=Count('id', filter=Q(winner=request.user))
        ).order_by('day')

        labels =[]
        total = []
        wins = []
        losses = []

        for row in by_day:
            labels.append(row['day'].strftime('%b %d'))
            total.append(row['total'])
            wins.append(row['wins'])
            losses.append(row['total'] - row['wins'])
        return Response({
            'labels': labels,
            'total': total,
            'wins': wins,
            'losses': losses, 
        })

        
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
                    "wins": int, 	#wins within selected period
                    "losses": int, 	#losses within selected period
                    "draws": int, 	#matches with winner=NULL
                    "degree": int, 	#unique opponents in this graph
                    "is_current": bool 	#true only for request.user
                }, 
                ...
            ],

            "edges": [
                {
                    "source": int, 	#node id, always cource < target
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
    - Known N+1 risk in Match queries 

    Permissions:
        IsAuthenticated
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
            #Implementation here
            pass

