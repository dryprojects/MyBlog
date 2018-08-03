#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      throttling.py 
@time:      2018/08/01 
""" 

from rest_framework import throttling


class PostUserRateThrottle(throttling.UserRateThrottle):
    rate = "30/minute"