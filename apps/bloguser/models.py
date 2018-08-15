import datetime
import collections

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from django.conf import settings

from dry_rest_permissions.generics import allow_staff_or_superuser

from bloguser.tasks import send_mail


MESSAGE_TIMEOUT = 1 #minutes 短信验证码过期时间


class UserProfile(AbstractUser):
    image = models.ImageField(verbose_name='用户头像', max_length=100, upload_to='bloguser/images/', default='bloguser/avatar.png', blank=True)
    #image_url是社会帐号下用户的头像url,这个只在请求用户头像时判断用户头像是否已经请求过所使用，不做验证
    image_url = models.CharField(verbose_name='用户头像url', max_length=100, default='')
    #重写email字段
    email = models.EmailField(_('邮箱'), unique=True)
    mobile_phone = models.CharField(verbose_name="手机号码", max_length=14, default="", null=True, blank=True)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def email_user(self, subject, message=None, from_email=None, html_msg=None, **kwargs):
        send_mail.delay(subject, message, from_email, [self.email], html_msg, **kwargs)

    def send_sms(self, **kwargs):
        """
        给用户发送短信
            这里我不做实现，如果你需要的话，可以参考云片等第三方服务商提供的sdk实现
            比较好的建议，新建立一个sms的app,对不同的服务商写不同的短信发送后端，通过一个统一的接口来调用
            用户可以在配置中自定义短信后端，来实现短信发送。
            如果对写这个app有兴趣，可以联系我。
        :param kwargs:
        :return: True 发送成功， False 发送失败 （这里最好返回一个 namedtuple 来提供更详细的信息）
        """
        return False

    def notify_user(self, content):
        """
        给用户创建一条后台通知
        :param content:
        :return:
        """
        from oper.models import Notification
        Notification.objects.create(user=self, content=content)

    def favorite(self, content_type, object_id):
        """
        用户收藏某类型对象
        :param content_type: 收藏类型
        :param object_id: 收藏对象id
        :return:
        """
        from oper.models import UserFavorite
        if UserFavorite.objects.filter(content_type=content_type, object_id=object_id).exists():
            return False
        UserFavorite.objects.create(user=self, content_type=content_type, object_id=object_id)
        return True

    def cancel_favorite(self, content_type, object_id):
        """
        取消收藏某类型对象
        :param content_type:
        :param object_id:
        :return:
        """
        from oper.models import UserFavorite
        queryset = UserFavorite.objects.filter(content_type=content_type, object_id=object_id)
        if queryset.exists():
            queryset.delete()
            return True
        return False

    def get_n_unread(self):
        """获取用户未读消息数"""
        from oper.tasks import get_n_unread
        return get_n_unread(self.pk)

    def on_avatar_changed(self):
        if not self.image_url:
            return
        avatar_changed = (self.image != 'bloguser/avatar.png') and not self.image_url.endswith(str(self.image))
        if avatar_changed:
            image_url = '%sbloguser/images/%s' % (settings.MEDIA_URL, self.image) if not str(self.image).startswith(
                'bloguser/images') else '%s%s' % (settings.MEDIA_URL, self.image)
            self.image_url = image_url

    def save(self, *args, **kwargs):
        self.on_avatar_changed()
        super().save(*args, **kwargs)

    def check_payment_status(self, goods_sn):
        """
        检测商品支付状态
        :param goods_sn: 商品序列号
        :return: True 已支付, False 未支付
        """
        from trade.models import PaymentLogs

        return PaymentLogs.objects.filter(user=self, goods_sn=goods_sn).exists()

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return request.user == self


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
    def send_message_auth_code(cls, message_code, mobile_phone, **kwargs):
        """
        发送短信验证码
            这里不做实现， 请参考第三方服务商提供的sdk实现
        """
        Result = collections.namedtuple('Result', ['success', 'detail'])

        return Result(False, '该方法未实现')

    @classmethod
    def remove_expired(cls):
        cls.objects.filter(expiration__lte=timezone.now()).delete()

    @property
    def is_expired(self):
        return self.expiration <= timezone.now()