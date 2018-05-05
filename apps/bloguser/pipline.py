#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      pipline.py 
@time:      2018/05/05 
""" 

from django.contrib.auth import get_user_model

from bloguser.utils import get_image_from_url

from uuid import uuid4


User = get_user_model()


def save_bloguser_extra_profile(backend, user, response, *args, **kwargs):
    """
    see more:
        http://python-social-auth.readthedocs.io/en/latest/use_cases.html#retrieve-google-friends
        http://python-social-auth.readthedocs.io/en/latest/pipeline.html
    :param backend:
    :param user:
    :param response:
    :param args:
    :param kwargs:
    :return:
    """
    if backend.name == 'github':
        #这里获取保存用户github的头像
        if user.image_url is '':
            image_url = response.get('avatar_url')
            image_file = get_image_from_url(image_url)
            if image_file is not None:
                #给头像文件命名采用uuid
                avatar_name = 'avatar' + uuid4().hex[:16]
                user.image.save(avatar_name, image_file)
                user.image_url = image_url
                user.save()