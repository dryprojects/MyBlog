#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      filters.py 
@time:      2018/08/04 
"""

from bloguser.models import UserProfile

from django_filters import rest_framework as filters
from dry_rest_permissions.generics import DRYPermissionFiltersBase


class UserFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        return queryset


class UserFilter(filters.FilterSet):
    class Meta:
        model = UserProfile
        fields = {
            'username': ['icontains'],
            'email': ['iexact']
        }


class UserFavoriteFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)
