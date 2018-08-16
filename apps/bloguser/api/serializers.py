#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      serializers.py 
@time:      2018/07/29 
"""

import re
import datetime
import random

from rest_framework import serializers
from django.contrib.auth import password_validation

from djoser import serializers as dj_serializers
from generic_relations.relations import GenericRelatedField

from bloguser.models import UserProfile, MessageAuthCode
from blog.models import Post
from blog.api.serializers import PostListSerializer
from oper.models import UserFavorite


class UserDetailSerializer(dj_serializers.UserSerializer):
    class Meta(dj_serializers.UserSerializer.Meta):
        fields = (
            'username',
            'email',
            'mobile_phone',
            'image'
        )
        read_only_fields = ('image',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["url", 'username', 'image']
        extra_kwargs = {
            'url': {'view_name': "userprofile-detail", 'read_only': True}
        }


class MessageAuthCodeSerializer(serializers.Serializer):
    phone_num = serializers.CharField(max_length=11)

    def generate_message_auth_code(self, count=6):
        """
        生成6位数的随机短信验证码
        :return:
        """
        return "".join([random.choice('1234567890') for i in range(int(count))])

    def validate_phone_num(self, phone_num):
        """
        验证手机号码
        :param phone_num:
        :return:
        """
        # 手机号码是否已经注册
        if UserProfile.objects.filter(mobile_phone=phone_num).exists():
            raise serializers.ValidationError('该手机号码已经注册过了')

        # 手机号码是否合法（国内）
        mobile_regex = r"1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        if not re.match(mobile_regex, phone_num):
            raise serializers.ValidationError('手机号码非法')

        # 短信验证码是否发送过快
        MessageAuthCode.remove_expired()
        if MessageAuthCode.objects.filter(phone_num=phone_num).exists():
            raise serializers.ValidationError('验证码发送过快')

        return phone_num

    def create(self, validated_data):
        """
        发送验证码
        :param validated_data:
        :return:
        """
        message_code = self.generate_message_auth_code()
        res = MessageAuthCode.send_message_auth_code(
            message_code=message_code,
            mobile_phone=validated_data['phone_num'])

        if not res.success:
            raise serializers.ValidationError(res.detail)

        return MessageAuthCode.objects.create(code=message_code, phone_num=validated_data['phone_num'])


class UserCreateSerializer(dj_serializers.UserCreateSerializer):
    """
    添加短信验证码验证
    """
    message_code = serializers.CharField(max_length=6, min_length=6, required=True, write_only=True)

    class Meta(dj_serializers.UserCreateSerializer.Meta):
        fields = dj_serializers.UserCreateSerializer.Meta.fields + ('mobile_phone', 'message_code')

    def validate(self, attrs):
        code = attrs.get('message_code')
        phone_num = attrs.get('mobile_phone')

        auth_codes = MessageAuthCode.objects.filter(code=code, phone_num=phone_num)
        if not auth_codes.exists():
            raise serializers.ValidationError({'message_code': '短信验证码错误'})

        if auth_codes.last().is_expired:
            MessageAuthCode.remove_expired()
            raise serializers.ValidationError({'message_code': '短信验证码已经过期'})

        if auth_codes.last().code != code:
            raise serializers.ValidationError({'message_code': '短信验证码错误'})

        del attrs['message_code']

        return super().validate(attrs)


class UserFavoriteSerializer(serializers.ModelSerializer):
    content_object = GenericRelatedField({
        Post: PostListSerializer()
    })

    class Meta:
        model = UserFavorite
        fields = ('content_object', 'add_time')
