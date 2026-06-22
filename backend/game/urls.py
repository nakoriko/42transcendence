# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    urls.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/05 11:46:05 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/21 17:27:40 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.urls import path
from .views import StartMatchView, LogMatchEventView, FinishMatchView, MatchHistoryView, InvitetMatchView, UpdateMatchStatusView

urlpatterns = [
    path ('match/start/', StartMatchView.as_view(), name='start_match'),
    path('matches/invite/', InvitetMatchView.as_view(), name='invite_match'),
    path('matches/<int:match_id>/status/', UpdateMatchStatusView.as_view(), name='update_match_status'),

    path('match/events/', LogMatchEventView. as_view(), name='log_match_event'),
    path('match/<int:match_id>/finish/', FinishMatchView.as_view(), name='finish_match'),
    path('matches/', MatchHistoryView.as_view(), name='match_history'), 
]