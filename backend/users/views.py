# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    views.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/01 22:15:42 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/06 12:30:49 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.shortcuts import render
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import status, generics

from rest_framework.permissions import IsAuthenticated
from .models import User, FriendRelation

from django.db.models import Q

from .serializers import RegisterSerializer, AvatarSerializer,  \
FriendRelationSerializer, FriendUserSerializer

# Complex end-point, a lot of logiic -> class + APIView

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response (serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        return Response({"message": "Logged out"}, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated] #define by standart method of rest framaework.permissions (checks token)
    def get(self, request):
        return Response({
            "id": request.user.id,
            "email": request.user.email,
            "nickname": request.user.nickname,
            "wins": request.user.wins,
            "losses": request.user.losses,
            "avatar": request.user.avatar.url if request.user.avatar else None,
        })


class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
            users = User.objects.exclude(id=request.user.id)
            data = [
                {"id": u.id, "nickname": u.nickname}
                for u in users
            ]
            return Response(data)

#updates for existing user 
class AvatarUploadView(generics.UpdateAPIView):
    serializer_class = AvatarSerializer
    permission_classes = [IsAuthenticated]

#returns same object to same user
    def get_object(self):
        #puts user which was got from jwt
        return self.request.user

#FRIEND_RELATION:

class FriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        to_user_id = request.data.get('to_user_id')

        #cannot add myself:
        if int (to_user_id) == request.user.id:
            return Response({'error': 'Cannot add yourself'}, status=400)
        
        #check if there's active invitations
        already_exits = FriendRelation.objects.filter(
            Q(from_user=request.user, to_user_id=to_user_id) |
            Q(from_user_id=to_user_id, to_user=request.user)
        ).exists()

        if already_exits:
            return Response({'error': 'Realtion  already exists'}, status=400)

        FriendRelation.objects.create (
            from_user=request.user,
            to_user_id=to_user_id,
            status='pending'
        )
        return Response({'message': 'Request sent succsessfully'}, status=201)

class FriendsListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        #filter all relations where "self" is presented
        friends = FriendRelation.objects.filter(
            Q(from_user = request.user) | Q(to_user=request.user), 
            status='accepted'
        )

        incoming = FriendRelation.objects.filter(
            to_user=request.user,
            status='pending'
        )
        return Response({
            'friends': FriendRelationSerializer (
                friends, many=True, context={'request': request}
            ).data, 
            'incoming': FriendRelationSerializer(
                incoming, many=True, context={'request': request}
            ).data,
        })

class FriendDetailView(APIView):
    permission_classes = [IsAuthenticated]
    #check is self is a part of relation
    def get_object(self, pk, user):
        try:
            return FriendRelation.objects.get (
                Q(from_user=user) | Q(to_user=user),
                pk=pk
            )
        except FriendRelation.DoesNotExist:
                return None

    #accpet and reject
    def patch(self, request, pk):
        relation = self.get_object(pk, request.user)
        if not relation:
                return Response({'error': 'Not Found'}, status=404)

        action = request.data.get('action')
        if action == 'accept':
            relation.status = 'accepted'
        elif action == 'reject':
            relation.status = 'rejected'
        else:
            return Response({'error': 'Invalid action'}, status=400)
        relation.save()
        return Response({'message': 'Done'}, status=200)

    #delete
    def delete(self, request, pk):
        relation = self.get_object(pk, request.user)
        if not relation:
            return Response({'error': 'Not found'}, status=404)
        relation.delete()
        return Response(status=204)