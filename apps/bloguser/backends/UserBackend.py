#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      UserBackend.py 
@time:      2018/05/04 
""" 

# from django.contrib.auth.hashers import check_password
# from django.contrib.auth import get_user_model
# from django.db.models import Q
#
#
# User = get_user_model()
#
#
# class UserBackend:
#     """
#     Authenticate against the User email or Username
#     see more:
#         https://docs.djangoproject.com/en/2.0/topics/auth/customizing/
#     """
#
#     def authenticate(self, request, username=None, password=None):
#         try:
#             user = User.objects.get(Q(username=username)|Q(email=username))
#             if user.check_password(password):
#                 return user
#             return None
#         except Exception as e:
#             return None
#
#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None