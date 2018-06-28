#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      tasks.py 
@time:      2018/06/23 
""" 

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

