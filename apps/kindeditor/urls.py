#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      urls.py 
@time:      2018/04/30 
""" 

from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from kindeditor.views import ImageFileUpload

app_name = 'kindeditor'

urlpatterns = [
    path('upload/', csrf_exempt(ImageFileUpload.as_view()), name='upload')
]