from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Match, MatchEvent
from .serializers import MatchCreateSerializer, MatchEventSerializer, MatchFinishSerializer


class StartMatchView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = MatchCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogMatchEventView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
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

