import datetime

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models

from bloguser.tasks import send_mail


MESSAGE_TIMEOUT = 1 #minutes 短信验证码过期时间


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

    def check_payment_status(self, goods_sn):
        """
        检测商品支付状态
        :param goods_sn: 商品序列号
        :return: True 已支付, False 未支付
        """
        from trade.models import PaymentLogs

        return PaymentLogs.objects.filter(user=self, goods_sn=goods_sn).exists()


class MessageAuthCode(models.Model):
    """
    手机短信验证码
    """
    code = models.CharField(verbose_name='短信验证码', max_length=6)
    phone_num = models.CharField(verbose_name='接收手机号', max_length=14)
    add_time = models.DateTimeField(verbose_name='手机验证码产生时间', default=datetime.datetime.now)
    expiration = models.DateTimeField(verbose_name='过期时间', blank=True, null=True)

    def __str__(self):
        return "%s/%s/%s/%s"%(self.phone_num, self.code, self.add_time, self.expiration)

    class Meta:
        verbose_name = '手机短信验证码'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if not self.expiration:
            self.expiration = timezone.now() + datetime.timedelta(minutes=int(MESSAGE_TIMEOUT))
        super(MessageAuthCode, self).save(*args, **kwargs)

    @classmethod
    def remove_expired(cls):
        cls.objects.filter(expiration__lte=timezone.now()).delete()