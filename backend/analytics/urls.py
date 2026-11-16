# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    urls.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/28 19:07:41 by nakoriko          #+#    #+#              #
#    Updated: 2026/10/02 18:06:04 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.urls import path
from .views import PongUniverseView, PlayerGraphView

urlpatterns = [
    path('universe/', PongUniverseView.as_view(), name='pong_universe'),
    path('player-graph/', PlayerGraphView.as_view(), name='player-graph'),

]