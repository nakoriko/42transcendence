# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    urls.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/01 22:10:00 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/17 15:43:56 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.urls import path
from .views import RegisterView, LogoutView, ProfileView, UserListView, AvatarUploadView, \
FriendRequestView, FriendsListView, FriendDetailView, PublicProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    #since router waits for a function as a 2nd paarameter, we pass our class converted in function
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),  #token creates by this, and we dont need to create login view
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('list/', UserListView.as_view(), name='users_list'),
    path ('avatar/', AvatarUploadView.as_view(), name='avatar_upload'),
    path('friends/', FriendsListView.as_view(), name='friends_list'),
    path('friends/request/', FriendRequestView.as_view(), name='friend_request'),
    path('friends/<int:pk>/', FriendDetailView.as_view(), name='friend_detail'),
    path('<int:pk>/', PublicProfileView.as_view(), name = 'public_profile'), 
]