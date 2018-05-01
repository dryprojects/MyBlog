#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      urls.py 
@time:      2018/05/01 
""" 

from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from mdeditor.views import ImageUploadView


app_name = 'mdeditor'

urlpatterns = [
    path('upload/', csrf_exempt(ImageUploadView.as_view()), name='upload')
]