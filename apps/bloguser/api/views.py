#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      views.py 
@time:      2018/07/29 
""" 

from bloguser import models
from bloguser.api import serializers, throttling, filters as user_filters

from rest_framework import viewsets, throttling as rest_throttling
from django_filters import rest_framework as filters

from dry_rest_permissions.generics import DRYPermissions


class UserViewset(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all()
    permission_classes = (DRYPermissions, )
    throttle_classes = (throttling.UserRateThrottle, )
    filter_backends = (filters.DjangoFilterBackend, user_filters.UserFilterBackend)
    filter_class = user_filters.UserFilter

    def get_serializer_class(self):
        if self.action in ["list"]:
            return serializers.UserSerializer
        elif self.action in ["retrieve"]:
            return serializers.UserDetailSerializer
        else:
            return serializers.UserWriteSerializer