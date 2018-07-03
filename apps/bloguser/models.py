from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models

from bloguser.tasks import send_mail


class UserProfile(AbstractUser):
    image = models.ImageField(verbose_name='用户头像', max_length=100, upload_to='bloguser/images/%Y/%m', default='bloguser/avatar.png', blank=True)
    #image_url是社会帐号下用户的头像url,这个只在请求用户头像时判断用户头像是否已经请求过所使用，不做验证
    image_url = models.CharField(verbose_name='用户头像url', max_length=100, default='')
    #重写email字段
    email = models.EmailField(_('邮箱'), blank=True, unique=True, null=True, help_text='邮箱是唯一的')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def email_user(self, subject, message=None, from_email=None, html_msg=None, **kwargs):
        send_mail.delay(subject, message, from_email, [self.email], html_msg, **kwargs)

    def notify_user(self, content):
        """
        给用户创建一条后台通知
        :param content:
        :return:
        """
        from oper.models import Notification
        Notification.objects.create(user=self, content=content)

    def get_n_unread(self):
        """获取用户未读消息数"""
        from oper.tasks import get_n_unread
        return get_n_unread(self.pk)

    def save(self, *args, **kwargs):
        """
        如果是本地用户，则把本地头像url存在image_url
        如果是第三方用户，则不做处理，直接使用获取的第三方的image_url
        :param args:
        :param kwargs:
        :return:
        """
        super().save(*args, **kwargs)

        if self.image.url is not None:
            self.image_url = self.image.url

        super().save(*args, **kwargs)