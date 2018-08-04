#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      serializers.py 
@time:      2018/07/29 
""" 

from bloguser.models import UserProfile

from rest_framework import serializers


class UserDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        exclude = (
            'password',
            'is_superuser',
            'is_staff',
            'is_active',
            'groups',
            'user_permissions'
        )
        extra_kwargs = {
            'url':{'view_name':'bloguser:user-detail'}
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'image']