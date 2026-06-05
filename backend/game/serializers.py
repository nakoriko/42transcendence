# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    serializers.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/05 11:41:07 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/05 15:40:40 by nakoriko         ###   ########.fr        #
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
