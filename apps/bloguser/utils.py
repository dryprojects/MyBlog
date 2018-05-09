#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      utils.py 
@time:      2018/05/05 
""" 

import requests

from django.core.files.base import ContentFile


def get_image_from_url(img_url):
    """
    从图片的地址，下载图片并返回对应ImageFile对象
    :param img_url:
    :return:
    """
    response = requests.get(img_url)
    if response.status_code == 200:
        img_file = ContentFile(response.content)
        return img_file

    return None