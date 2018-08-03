#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      routers.py 
@time:      2018/08/03 
""" 

from rest_framework import routers


class PostRouter(routers.DefaultRouter):
    root_view_name = "post-api-root"