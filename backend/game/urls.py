# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    urls.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/05 11:46:05 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/05 15:36:27 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.urls import path
from .views import StartMatchView, LogMatchEventView, FinishMatchView

urlpatterns = [
    path ('match/start/', StartMatchView.as_view(), name='start_match'),
    path('match/events/', LogMatchEventView. as_view(), name='log_match_event'),
    path('match/<int:match_id>/finish/', FinishMatchView.as_view(), name='finish_match')
]