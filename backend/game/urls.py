# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    urls.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/05 11:46:05 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/28 19:16:39 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.urls import path
from .views import StartMatchView, FinishMatchView, \
        MatchHistoryView, MatchEventsView, BulkMatchEventView

urlpatterns = [
    path ('matches/start/', StartMatchView.as_view(), name='start_match'),

    path('matches/events/bulk/', BulkMatchEventView.as_view(), name='bulk_events'),
    path('matches/<int:match_id>/events/', MatchEventsView.as_view(), name='match_events'),

    path('matches/<int:match_id>/finish/', FinishMatchView.as_view(), name='finish_match'),
    path('matches/', MatchHistoryView.as_view(), name='match_history'), 
]