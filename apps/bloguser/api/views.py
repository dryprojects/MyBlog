#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      views.py 
@time:      2018/07/29 
""" 

from django.urls.exceptions import NoReverseMatch

from rest_framework import viewsets, throttling as rest_throttling
from rest_framework import mixins, permissions, reverse, response, status
from django_filters import rest_framework as filters

from dry_rest_permissions.generics import DRYPermissions
from djoser import views
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from bloguser import models
from bloguser.api import serializers, throttling, filters as user_filters


class MessageAuthCodeViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    create:
    给指定手机号码发送验证码
    """
    queryset = models.MessageAuthCode.objects.all()
    serializer_class = serializers.MessageAuthCodeSerializer
    permission_classes = (permissions.AllowAny, )