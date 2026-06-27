from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg #object to calculate aberege reaction_time for all users
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Match, MatchEvent
from datetime import timedelta 
from django.utils import timezone

from .serializers import MatchCreateSerializer, MatchEventSerializer, MatchFinishSerializer, \
    MatchHistorySerializer, MatchInviteSerializer

User = get_user_model()

# USe just for local mode:
class StartMatchView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = MatchCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(status=Match.Status.ACTIVE, mode=Match.Mode.LOCAL)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Use for websocket (invites people top game)
class InvitetMatchView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        opponent_id = request.data.get ('opponent_id')
        try:
            opponent = User.objects.get(id=opponent_id)
        except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MatchInviteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                player1=request.user,
                player2=opponent,
                status=Match.Status.PENDING,
                mode=Match.Mode.REMOTE)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateMatchStatusView(APIView):
    permission_classes =[IsAuthenticated]
    def patch(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id) #takes id from database and creates object match
        except Match.DoesNotExist:
            return Response({'error': 'Match not found'}, status=status.HTTP_404_NOT_FOUND)
        match.status=request.data.get('status') #saves actual status for match
        match.save()
        return Response({'id': match.id, 'status':match.status})

class LogMatchEventView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        opponent_id = request.data
        serializer = MatchEventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response (serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FinishMatchView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, match_id):
        try: #not necessary in outr case, but good practice: check if object exists
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({'error': 'Match not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MatchFinishSerializer(match, data=request.data, partial=True) #without partial - jango wants all fields
        if serializer.is_valid():
            serializer.save()
            # serializer.save( updates just fields which frontend sent with http reequest (scores, winner, endet at)
            #backend should update status as well
            match.status = Match.Status.FINISHED
            match.save(update_fields=['status'])
            winner = match.winner
            loser = match.player1 if match.winner == match.player2 else match.player2
            winner.wins += 1
            loser.losses += 1
            winner.save()
            loser.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MatchEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, match_id):
        match = get_object_or_404(Match, id=match_id)

        if request.user != match.player1 and request.user != match.player2:
            return Response(status=403)
        events = MatchEvent.objects.filter (match=match).order_by('timestamp')
        serializer = MatchEventSerializer(events, many=True)
        return Response(serializer.data)

class MatchHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        matches = Match.objects.filter(
            Q(player1=request.user) | Q(player2=request.user),
            ended_at__isnull=False
        ).order_by('-ended_at')[:limit]

        serializer = MatchHistorySerializer(matches, many=True, context={'request': request})
        return Response(serializer.data)

class AllUserEventsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        matches = Match.objects.filter(
            Q(player1=request.user) | Q(player2=request.user),
            ended_at__isnull=False
        )
        events = MatchEvent.objects.filter(
            match__in=matches
        ).order_by('match_id', 'timestamp')

        serializer = MatchEventSerializer(events, many=True)
        return Response(serializer.data)

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

        


