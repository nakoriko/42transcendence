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
from .views import StartMatchView, LogMatchEventView, FinishMatchView, \
        MatchHistoryView, InviteMatchView, UpdateMatchStatusView, MatchEventsView, \
        AllUserEventsView, BulkMatchEventView

urlpatterns = [
    path ('matches/start/', StartMatchView.as_view(), name='start_match'),
    path('matches/invite/', InviteMatchView.as_view(), name='invite_match'),
    path('matches/<int:match_id>/status/', UpdateMatchStatusView.as_view(), name='update_match_status'),

    path('matches/events/', LogMatchEventView.as_view(), name='log_match_event'),
    path('matches/events/bulk/', BulkMatchEventView.as_view(), name='bulk_events'),
    path('matches/<int:match_id>/events/', MatchEventsView.as_view(), name='match_events'),

    path('matches/<int:match_id>/finish/', FinishMatchView.as_view(), name='finish_match'),
    path('matches/', MatchHistoryView.as_view(), name='match_history'), 

    path ('events/', AllUserEventsView.as_view(), name='all_user_events'),
    # path('analytics/universe/', PongUniverseView.as_view(), name='pong_universe'),
]