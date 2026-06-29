# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    views.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/28 19:13:36 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/28 20:09:50 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.contrib.auth import get_user_model
# from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Avg #object to calculate aberege reaction_time for all users
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from game.models import Match, MatchEvent
from datetime import timedelta 
from django.utils import timezone

User = get_user_model()

class PongUniverseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', 'all') #7 days /30 d/ all, readds from ?period=7d from url
        since = None
        if(period == '7d'):
            since = timezone.now() - timedelta(days=7)
        elif (period == '30d'):
            since = timezone.now() - timedelta(days=30)

        users = User.objects.all().order_by('date_joined')
        result = []

        for user in users:
            match_qs = Match.objects.filter(
                Q(player1=user) | Q(player2=user),
                status=Match.Status.FINISHED
            )
            if since:
                match_qs = match_qs.filter(ended_at__gte=since)
            total = match_qs.count()
            wins = match_qs.filter(winner=user).count()
            event_qs = MatchEvent.objects.filter(match__in=match_qs, player=user)
            hits = event_qs.filter(event_type=MatchEvent.EventType.HIT).count()
            misses = event_qs.filter(event_type=MatchEvent.EventType.MISS).count()

            avg_reaction = event_qs.filter(
                event_type=MatchEvent.EventType.HIT,
                reaction_time_ms__isnull=False
            ).aggregate(avg=Avg('reaction_time_ms'))['avg']

            result.append({
                'id': user.id,
                'nickname': user.nickname or user.email,
                'date_joined': user.date_joined.isoformat(),
                'total_matches': total,
                'wins': wins,
                'losses': total - wins,
                'win_rate': round(wins / total, 2) if total > 0 else 0,
                'avg_reaction_ms': round(avg_reaction) if avg_reaction else None,
                'hit_accuracy': round(hits / (hits + misses), 2) if (hits + misses) > 0 else None,
            })
        return Response(result)

class PlayerStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', 'all')
        since = None
        if period == '7d':
            since = timezone.now() - timedelta(days=7)
        elif period =='30d':
            since = timezone.now() - timedelta(days=30)
        
        matches = Match.objects.filter(
            Q(player1=request.user) | Q(player2=request.user),
            status=Match.Status.FINISHED
        )
        if since:
                matches = matches.filter(ended_at__gte=since)
        
        #group by days via annotate
        #by_day  - query set of days with date, total matches and wins fro every sorted day
        by_day = matches.annotate(
            day=TruncDate('ended_at')
        ).values('day').annotate(
            total=Count('id'),
            wins=Count('id', filter=Q(winner=request.user))
        ).order_by('day')

        labels =[]
        total = []
        wins = []
        losses = []

        for row in by_day:
            labels.append(row['day'].strftime('%b %d'))
            total.append(row['total'])
            wins.append(row['wins'])
            losses.append(row['total'] - row['wins'])
        return Response({
            'labels': labels,
            'total': total,
            'wins': wins,
            'losses': losses, 
        })

        


