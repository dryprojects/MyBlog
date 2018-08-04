#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      views.py 
@time:      2018/07/29 
""" 

from bloguser import models
from bloguser.api import serializers

from rest_framework import viewsets


class UserViewset(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserDetailSerializer