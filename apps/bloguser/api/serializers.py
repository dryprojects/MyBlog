#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      serializers.py 
@time:      2018/07/29 
"""

from bloguser.models import UserProfile

from rest_framework import serializers
from django.contrib.auth import password_validation

from djoser.serializers import UserSerializer as DJ_UserSerializer


class UserDetailSerializer(DJ_UserSerializer):
    class Meta(DJ_UserSerializer.Meta):
        fields = (
            'username',
            'email',
            'mobile_phone',
            'image'
        )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["url", 'username', 'image']
        extra_kwargs = {
            'url': {'view_name': "userprofile-detail", 'read_only': True}
        }
