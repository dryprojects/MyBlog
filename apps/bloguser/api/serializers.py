#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      serializers.py 
@time:      2018/07/29 
"""

from bloguser.models import UserProfile

from rest_framework import serializers


class UserWriteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'username',
            'email',
            'mobile_phone',
            'image',
            'password'
        )
        extra_kwargs = {
            'url': {'view_name': 'bloguser:user-detail'}
        }

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user



class UserDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'username',
            'email',
            'mobile_phone',
            'image'
        )
        extra_kwargs = {
            'url': {'view_name': 'bloguser:user-detail'}
        }
        read_only_fields = ('mobile_phone', 'image')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["url", 'username', 'image']
        extra_kwargs = {
            'url': {'view_name': "bloguser:user-detail", 'read_only': True}
        }
