#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      urls.py 
@time:      2018/05/04 
""" 

from django.urls import path, include

from bloguser import views


app_name = 'bloguser'

urlpatterns = [
    path('login/', views.BlogUserLoginView.as_view(), name='bloguser-login'),
    path('logout/', views.BlogUserLogutView.as_view(), name='bloguser-logout'),
    path('register/', views.BlogUserRegisterView.as_view(), name='bloguser-register'),
    path('active/<str:uidb64>/<str:token>/', views.BlogUserActiveConfirmView.as_view(), name='bloguser-active')
]