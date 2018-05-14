#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      context_processors.py 
@time:      2018/05/03 
""" 

from blog.models import Post, Tag, Category
from oper.models import BlogOwner, FriendshipLinks


def post_extra(request):
    context = {}
    post_queryset = Post.objects.all()
    #按月份归档
    post_archive_date_list = post_queryset.dates('published_time', 'month', order='DESC')
    context['post_archive_date_list'] = post_archive_date_list
    #所有博文的标签
    post_tag_list = Tag.objects.all()
    context['post_tag_list'] = post_tag_list
    #所有的博文分类
    cts = Category.objects.all()
    context['post_category_list'] = cts
    #好评最多的 喜欢数排序
    #热门博文 浏览数排序
    #博主推荐
    blogowner = BlogOwner.objects.first()
    recommend_posts = blogowner.recommend_posts.all()
    context['recommend_posts'] = recommend_posts
    #友情链接
    friendship_links = FriendshipLinks.objects.all()[:10]
    context['friendship_links'] = friendship_links
    #公告
    blog_notifications = post_queryset.filter(type='notification')[:3]
    context['blog_notifications'] = blog_notifications
    #博主信息
    context['blog_owner'] = blogowner

    return context