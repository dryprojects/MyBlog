#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      serializers.py 
@time:      2018/05/03 
""" 

from rest_framework import serializers

from blog.models import Category


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, parent):
        queryset = parent.get_children()
        serializer = CategoryTreeSerializer(queryset, many=True, read_only=True, context=self.context)

        return serializer.data

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'children']