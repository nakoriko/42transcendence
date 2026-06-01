from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    nickname = models.CharField(max_length=50, blank = True)
    avatar = models.ImageField(upload_to='avatars/', blank = True)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    is_online = models.BooleanField(default=False)

class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='matches_as_player1')
    player2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='matches_as_player2')
    score_player1 = models.IntegerField(default=0)
    score_player2 = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_matches')

class MatchEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=10)
    player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='match_events')
    timestamp = models.DateTimeField(auto_now_add=True)


class FriendRelation(models.Model):
    from_user =  models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    to_user =  models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invites')
    status = models.CharField(max_length=10, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)



