# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    serializers.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/05 11:41:07 by nakoriko          #+#    #+#              #
#    Updated: 2026/10/16 17:38:09 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from rest_framework import serializers
from .models import Match, MatchEvent

class MatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'status', 'mode', 'player1', 'player2', 'started_at']
        read_only_fields = ['id', 'status', 'mode', 'player1', 'started_at']
        extra_kwargs = {'player2': {'required': True, 'allow_null': False}}

class MatchEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchEvent
        fields = ['id', 'match', 'event_type', 'player', 'timestamp', 'pos_x', 'pos_y', 'reaction_time_ms']
        read_only_fields= ['id', 'timestamp']

class MatchEventInputSerializer(serializers.Serializer):
    match = serializers.IntegerField()
    player = serializers.IntegerField(allow_null=True, required=False)
    event_type=serializers.ChoiceField(choices=MatchEvent.EventType.choices)
    pos_x = serializers.FloatField(allow_null=True, required=False)
    pos_y = serializers.FloatField(allow_null=True, required=False)
    reaction_time_ms = serializers.IntegerField(allow_null=True, required=False)

class MatchFinishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['winner', 'score_player1', 'score_player2']

class MatchHistorySerializer(serializers.ModelSerializer):
    opponent_nickname = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()


    class Meta:
        model = Match
        fields = ['id', 'opponent_nickname', 'score', 'result', 'ended_at', 'status']
    
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
        if obj.winner_id is None:
            return 'draw'
        return 'win' if obj.winner_id == request_user.id else 'loss'


