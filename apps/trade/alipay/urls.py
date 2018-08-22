#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      urls.py 
@time:      2018/08/21 
"""

from django.urls import path, re_path, include

from trade.alipay import views

app_name = 'alipay'

urlpatterns = [
    path('alipay/return/', views.AlipayAPIView.as_view(), name='alipay-return')
]



