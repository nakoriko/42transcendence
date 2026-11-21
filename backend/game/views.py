from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Match, MatchEvent
from django.utils import timezone
from ws.notify import notify_group

from .serializers import MatchCreateSerializer, MatchEventSerializer, MatchFinishSerializer, \
    MatchHistorySerializer, MatchEventInputSerializer 

User = get_user_model()

# USe just for local mode:
class StartMatchView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = MatchCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.validated_data['player2'] == request.user:
            return Response({'error': 'Cannot play againts yourself'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(player1=request.user, status=Match.Status.ACTIVE, mode=Match.Mode.LOCAL)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FinishMatchView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, match_id):
        try: #not necessary in outr case, but good practice: check if object exists
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({'error': 'Match not found'}, status=status.HTTP_404_NOT_FOUND)
        #protection from changing match status by other users
        if(request.user != match.player1 and request.user != match.player2):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        if(match.status == Match.Status.FINISHED):
            return Response({'error': 'Match is already finished'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MatchFinishSerializer(match, data=request.data, partial=True) #without partial - jango wants all fields
        if serializer.is_valid():
            winner = serializer.validated_data.get('winner')
            if winner is None or winner.id not in (match.player1_id, match.player2_id):
                return Response({'error': 'Winner must be a participant of the match'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            # serializer.save( updates just fields which frontend sent with http reequest (scores, winner, endet at)
            #backend should update status as well
            match.status = Match.Status.FINISHED
            match.ended_at=timezone.now()
            match.save(update_fields=['status', 'ended_at'])
            
            #F(): database adds + 1 itself, other user fieled are not overwritten
            loser_id = match.player1_id if match.winner_id == match.player2_id else match.player2_id
            User.objects.filter(pk=match.winner_id).update(wins=F('wins') + 1)
            User.objects.filter(pk=loser_id).update(losses=F('losses') + 1)

            # real-time dashboard update
            notify_group("dashboard_updates", {
                "type": "match_finished_event",
                "match_id": match.id,
                "player1_id": match.player1_id,
                "player2_id": match.player2_id,
                "winner_id": match.winner_id,
                "score_player1": match.score_player1,
                "score_player2": match.score_player2,
            })
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
    MAX_LIMIT = 200

    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 10))
        except ValueError:
            return Response({'error': 'limit must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        limit = max(1, min(limit, self.MAX_LIMIT))
        matches = (
            Match.objects
            .select_related('player1', 'player2', 'winner')
            .filter (
                Q(player1=request.user) | Q(player2=request.user),
                ended_at__isnull=False
            )
            .order_by('-ended_at')[:limit]
        )
        serializer = MatchHistorySerializer(matches, many=True, context={'request': request})
        return Response(serializer.data)

class BulkMatchEventView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = MatchEventInputSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        events = serializer.validated_data

        match_ids = { e['match'] for e in events}
        matches = Match.objects.in_bulk(match_ids)
        if len(matches) != len(match_ids):
            return Response({ 'error': 'Unknown match'},
            status=status.HTTP_400_BAD_REQUEST)

        for e in events:
            match = matches[e['match']]
            if request.user.id not in (match.player1_id, match.player2_id):
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            if match.status != Match.Status.ACTIVE:
                return Response({'error': 'Match is not active'}, status=status.HTTP_400_BAD_REQUEST)
            player_id = e.get('player')
            if player_id is not None and player_id not in (match.player1_id, match.player2_id):
                return Response({ 'error': 'Player is not a participant'}, status=status.HTTP_400_BAD_REQUEST)
        
        created = MatchEvent.objects.bulk_create([
            MatchEvent(
                match_id=e['match'],
                player_id=e.get('player'),
                event_type=e['event_type'],
                pos_x=e.get('pos_x'),
                pos_y=e.get('pos_y'),
                reaction_time_ms=e.get('reaction_time_ms')
            )
            for e in events
        ])
        return Response(MatchEventSerializer(created, many=True).data, status=status.HTTP_201_CREATED)
