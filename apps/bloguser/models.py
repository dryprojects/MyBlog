from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    image = models.ImageField(verbose_name='用户头像', max_length=100, upload_to='bloguser/images/%Y/%m', default='bloguser/avatar.png', blank=True)
    #image_url是社会帐号下用户的头像url,这个只在请求用户头像时判断用户头像是否已经请求过所使用，不做验证
    image_url = models.CharField(verbose_name='用户头像url', max_length=100, default='')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name