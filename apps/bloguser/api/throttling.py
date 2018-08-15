#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      throttling.py 
@time:      2018/08/04 
""" 

from rest_framework import throttling


class UserRateThrottle(throttling.UserRateThrottle):
    rate = "30/minute"