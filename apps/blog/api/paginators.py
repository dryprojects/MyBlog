#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      paginator.py 
@time:      2018/07/30 
""" 

from rest_framework import pagination


class PostPaginator(pagination.PageNumberPagination):
    page_size = 4
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 10
