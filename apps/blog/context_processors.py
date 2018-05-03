#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      context_processors.py 
@time:      2018/05/03 
""" 

from blog.models import Post


def post_extra(request):
    context = {}
    #按月份归档
    post_archive_date_list = Post.objects.dates('published_time', 'month', order='DESC')
    context['post_archive_date_list'] = post_archive_date_list

    return context