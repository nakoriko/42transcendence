# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    urls.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/28 19:07:41 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/28 20:11:12 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.urls import path
from .views import PongUniverseView, PlayerStatsView

urlpatterns = [
    path('universe/', PongUniverseView.as_view(), name='pong_universe'),
    path('player-stats/', PlayerStatsView.as_view(), name='player_stats'),

]