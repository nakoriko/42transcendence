# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    views.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/06/01 20:25:58 by nakoriko          #+#    #+#              #
#    Updated: 2026/06/01 22:16:07 by nakoriko         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #


from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Decorator (simple end point, one mehos)
@api_view(['GET'])
def hello_view(request):
    return Response({"message": "hello wwworld"})

# Complex end-point, a lot of logiic -> class + APIView
