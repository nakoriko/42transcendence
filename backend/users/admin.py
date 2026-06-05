from django.contrib import admin
from .models import User, FriendRelation

admin.site.register(User)
admin.site.register(FriendRelation)

# Register your models here.
