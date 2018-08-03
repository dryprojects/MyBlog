#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      fields.py 
@time:      2018/08/03 
""" 

from rest_framework import serializers


class CategoryParentField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset if not queryset else queryset.filter(author=self.context['request'].user)


class PostParentField(serializers.HyperlinkedRelatedField):
    def get_queryset(self):
        #这里返回用户自己的博文，以便于选择父级别博文时不至于选择到别人的博文
        queryset = super().get_queryset()
        return queryset if not queryset else queryset.filter(author=self.context['request'].user)