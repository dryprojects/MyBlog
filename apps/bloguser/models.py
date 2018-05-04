from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    image = models.ImageField(verbose_name='用户头像', max_length=100, upload_to='bloguser/images/%Y/%m', default='bloguser/avatar.png', blank=True)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name