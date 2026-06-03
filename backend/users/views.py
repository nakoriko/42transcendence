# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    views.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/01 22:15:42 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/03 10:39:45 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.shortcuts import render
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import status

from rest_framework.permissions import IsAuthenticated



from .serializers import RegisterSerializer

# Complex end-point, a lot of logiic -> class + APIView

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response (serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        return Response({"message": "Logged out"}, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated] #define by standart method of rest framaework.permissions (checks token)
    def get(self, request):
        return Response({
            "email": request.user.email,
            "nickname": request.user.nickname,
            "wins": request.user.wins,
            "losses": request.user.losses,
        })


from .models import Match, MatchEvent
from .serializers import MatchCreateSerializer, MatchEventSerializer

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