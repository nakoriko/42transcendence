from django.urls import path
from .views import PongUniverseView, PlayerGraphView

urlpatterns = [
    path('universe/', PongUniverseView.as_view(), name='pong_universe'),
    path('player-graph/', PlayerGraphView.as_view(), name='player-graph'),

]