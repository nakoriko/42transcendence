# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    serializers.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/05 11:41:07 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/16 11:51:25 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from rest_framework import serializers
from .models import Match, MatchEvent

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

class MatchFinishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['winner', 'score_player1', 'score_player2', 'ended_at']

class MatchHistorySerializer(serializers.ModelSerializer):
    opponent_nickname = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()


    class Meta:
        model = Match
        fields = ['id', 'opponent_nickname', 'score', 'result', 'ended_at']
    
    def get_opponent_nickname(self, obj):
        request_user = self.context['request'].user
        opponent = obj.player2 if obj.player1 == request_user else obj.player1
        return opponent.nickname if opponent else 'Unknown'

    def get_score(self, obj):
        request_user = self.context['request'].user
        if obj.player1 == request_user:
            return f"{obj.score_player1} - {obj.score_player2}"
        return f"{obj.score_player2} - {obj.score_player1}"

    def get_result(self, obj):
        request_user = self.context['request'].user
        return 'win' if obj.winner == request_user else 'loss'


