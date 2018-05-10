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
    path('active/<str:uidb64>/<str:token>/', views.BlogUserActiveConfirmView.as_view(), name='bloguser-active'),
    path('password-reset/', views.BlogUserPasswordResetView.as_view(), name='bloguser-password-reset'),
    path('password-reset-done', views.BlogUserPasswordResetDoneView.as_view(), name='bloguser-password-reset-done'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', views.BlogUserPasswordResetConfirmView.as_view(), name='bloguser-password-reset-confirm'),
    path('password-reset-complete/', views.BlogUserPasswordResetCompleteView.as_view(), name='bloguser-password-reset-complete')
]

urlpatterns += [
    path('usercenter/', views.BlogUserAccountView.as_view(), name='bloguser-usercenter')
]