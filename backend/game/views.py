from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Match, MatchEvent

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
            return Response({'error': 'Match not found'}, status=status_HTTP_404_NOT_FOUND)
        serializer = MatchFinishSerializer(match, data=request.data, partial=True) #without partial - jango wants all fields
        if serializer.is_valid():
            serializer.save()
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
