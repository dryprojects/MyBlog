#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      views.py 
@time:      2018/08/16 
"""

from rest_framework import viewsets, mixins, filters, permissions, status, response
from rest_framework.decorators import action
from dry_rest_permissions.generics import DRYGlobalPermissions

from trade import models
from trade.api import serializers, filters


class ShoppingCartViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
    当前用户的购物车内容列表
    """
    queryset = models.ShoppingCart.objects.all()
    serializer_class = serializers.ShoppingCartSerializer
    permission_classes = [permissions.IsAuthenticated, DRYGlobalPermissions]
    filter_backends = (filters.ShoppingCartFilterBackend,)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def clear_shoppingcart(self, request):
        """清空当前用户的购物车"""
        res = models.ShoppingCart.clear_shoppingcart(request.user)

        if not res.success:
            return response.Response({'detail': res.detail}, status=status.HTTP_400_BAD_REQUEST)

        return response.Response({"detail": res.detail}, status=status.HTTP_204_NO_CONTENT)
