# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    urls.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/05 11:46:05 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/05 11:51:06 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.urls import path
from .views import StartMatchView, LogMatchEventView

urlpatterns = [
    path ('match/start/', StartMatchView.as_view(), name='start_match'),
    path('match/events/', LogMatchEventView. as_view(), name='log_match_event'),
]