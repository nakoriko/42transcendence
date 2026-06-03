# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    serializers.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/01 19:41:01 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/03 10:25:10 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Match, MatchEvent

#say whetre to take user model to do not write path everytime when it changes
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    #never returns passwortdfor reading:
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'password', 'nickname']
    
    #validated_data - set of data after is_valid() of DRF
    #self same as this in c++
    #create - needs to override default create (from save()) to hash password
    #create_user() - Djangos User manager method that hashes password before saving
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nickname=validated_data['nickname'],
        )
        return user

class MatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'player1', 'player2', 'started_at']
        read_only_fields = ['id', 'started_at']

class MatchEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchEvent
        fields = ['id', 'match', 'event_type', 'player', 'timestamp', 'pos_x', 'pos_y', 'reaction_time_ms']
        read_only_fields= ['id', 'timestamp']
