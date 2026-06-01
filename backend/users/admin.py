from django.contrib import admin
from .models import User
from .models import Match, MatchEvent, FriendRelation

admin.site.register(User)
admin.site.register(Match)
admin.site.register(MatchEvent)
admin.site.register(FriendRelation)

# Register your models here.
