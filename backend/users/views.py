# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    views.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/01 22:15:42 by nakoriko          #+#    #+#              #
#    Updated: 2026/10/10 12:23:16 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import status, generics

from rest_framework.permissions import IsAuthenticated
from .models import User, FriendRelation

from django.db.models import Q

from .serializers import RegisterSerializer, AvatarSerializer,  \
FriendRelationSerializer, FriendUserSerializer, ProfileUpdateSerializer

#SABINO modifica per vedere richieste amicizia in tempo reale
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
           serializer.save()
           return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
            


class PublicProfileView(APIView):
    permission_classes = [IsAuthenticated] #define by standart method of rest framaework.permissions (checks token)
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return Response({
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "wins": user.wins,
            "losses": user.losses,
            "avatar": user.avatar.url if user.avatar else None,
        })


class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
            users = User.objects.exclude(id=request.user.id)
            friend_pairs = FriendRelation.objects.filter (
                    Q(from_user=request.user) | Q(to_user=request.user),
                    status='accepted'
            ).values_list('from_user_id', 'to_user_id')

            my_friend_ids = set() 
            for pair in friend_pairs:
                for uid in pair:
                    my_friend_ids.add(uid)
            
            my_friend_ids.discard(request.user.id)
            data = [
                {"id": u.id, 
                "nickname": u.nickname,
                "wins": u.wins,
                "is_online": u.is_online,
                "avatar": request.build_absolute_uri(u.avatar.url) if u.avatar else None,
                "is_friend": u.id in my_friend_ids,
                }
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

        if to_user_id is None:
                return Response({ 'error' : 'to_user_id is required'}, status=400)
        try:
            to_user_id = int(to_user_id)
        except (TypeError, ValueError):
            return Response({'error': 'to_user_id must be a valid integer'}, status=400)

        #cannot add myself:
        if to_user_id == request.user.id:
            return Response({'error': 'Cannot add yourself'}, status=400)
        
        if not User.objects.filter(pk=to_user_id).exists():
            return Response({'error': 'User not found'}, status=404)
        
        #check if there's active invitations
        existing = FriendRelation.objects.filter(
            Q(from_user=request.user, to_user_id=to_user_id) |
            Q(from_user_id=to_user_id, to_user=request.user)
        )

        if existing.exclude(status='rejected').exists():
            return Response({'error': 'Relation  already exists'}, status=400)
        existing.filter(status='rejected').delete()

        #SABINO modifica per vedere richieste amicizia in tempo reale
        relation = FriendRelation.objects.create (
            from_user=request.user,
            to_user_id=to_user_id,
            status='pending'
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f"user_{to_user_id}", {
            "type": "friend_request_event",
            "from_user_id": request.user.id,
            "from_user_nickname": request.user.nickname,
            "relation_id": relation.id,
        })
        
        return Response({'message': 'Request sent succsessfully'}, status=201)

class FriendsListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        #filter all relations where "self" is presented
        friends = (
            FriendRelation.objects
            .select_related('from_user', 'to_user')
            .filter(
                Q(from_user = request.user) | Q(to_user=request.user), 
                status='accepted'
            )
        )

        incoming = (
            FriendRelation.objects
            .select_related('from_user', 'to_user')
            .filter(
                to_user=request.user,
                status='pending'
            )
        )

        outgoing = (
            FriendRelation.objects
            .select_related('from_user', 'to_user')
            .filter(
                from_user=request.user,
                status='pending'
            ) 
        )
        return Response({
            'friends': FriendRelationSerializer (
                friends, many=True, context={'request': request}
            ).data, 
            'incoming': FriendRelationSerializer(
                incoming, many=True, context={'request': request}
            ).data,
            'outgoing': FriendRelationSerializer(
                outgoing, many=True, context={'request': request}
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
        if relation.to_user_id != request.user.id:
                return Response({'error': 'Only recipient can accept or reject'}, status=403)

        action = request.data.get('action')
        if action == 'accept':
            relation.status = 'accepted'
            #SABINO modifica per vedere richieste amicizia in tempo reale
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(f"user_{relation.from_user_id}", {
                "type": "friend_request_accepted_event",
                "user_id": request.user.id,
                "nickname": request.user.nickname,
            })
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