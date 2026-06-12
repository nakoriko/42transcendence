from django.db import models
from django.conf import settings

class Match(models.Model):
    player1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='matches_as_player1')
    player2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='matches_as_player2')
    score_player1 = models.IntegerField(default=0)
    score_player2 = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_matches')

class MatchEvent(models.Model):
    class EventType(models.TextChoices):
        HIT = 'hit', 'Ball hit paddle'
        MISS = 'miss', 'Ball missed paddle'
        GOAL = 'goal', 'Goal scored'

    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    event_type = models.CharField(
        max_length=10,
        choices=EventType.choices,
        default=EventType.HIT
    )
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='match_events')
    timestamp = models.DateTimeField(auto_now_add=True)

    pos_x = models.FloatField(null=True) #float because we use 0 ..1  resolution-independent across screens
    pos_y = models.FloatField(null=True) #existing rows have no coordinate data
    reaction_time_ms = models.IntegerField(null=True) #null: bounce events have no player reaction

