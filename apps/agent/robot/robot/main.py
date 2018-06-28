#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      main.py 
@time:      2018/06/23 
"""

import sys
import os

from scrapy.cmdline import execute

base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(base)

execute(['scrapy', 'crawl', 'jobbole'])