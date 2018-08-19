#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      filters.py 
@time:      2018/08/16 
""" 

from dry_rest_permissions.generics import DRYPermissionFiltersBase


class ShoppingCartFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)


class GoodsOrderFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)


class GoodsOrderRelationFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)