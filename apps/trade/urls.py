#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      urls.py 
@time:      2018/08/17 
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from trade.api import views as api_views


router = DefaultRouter()
router.register('shoppingcart', api_views.ShoppingCartViewSet)

app_name = 'trade'

urlpatterns = [
    path('', include(router.urls))
]
