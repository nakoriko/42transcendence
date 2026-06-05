# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    urls.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/01 22:10:00 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/05 11:51:03 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.urls import path
from .views import RegisterView, LogoutView, ProfileView
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    #since router waits for a function as a 2nd paarameter, we pass our class converted in function
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),  #token creates by this, and we dont need to create login view
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),

]