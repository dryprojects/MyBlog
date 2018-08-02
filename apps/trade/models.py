import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse

from trade import enums

# Create your models here.
User = get_user_model()


class Signer(models.Model):
    """
    商品签收人信息
    """
    name = models.CharField(verbose_name='签收人称呼', max_length=30)
    phone_num = models.CharField(verbose_name='联系电话', max_length=14)
    sign_time = models.DateTimeField(verbose_name='签收时间', default=datetime.datetime.now)

    def __str__(self):
        return "%s/%s/%s"%(self.name, self.phone_num, self.sign_time)

    class Meta:
        verbose_name = '商品签收人信息'
        verbose_name_plural = verbose_name


class ShoppingCart(models.Model):
    """
    购物车
    """
    user = models.ForeignKey(User, verbose_name='付费用户', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, verbose_name='商品类型', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(verbose_name='商品id')
    content_object = GenericForeignKey('content_type', 'object_id') #商品实体
    n_goods = models.PositiveIntegerField(verbose_name='商品购买数量', default=1)
    created_time = models.DateTimeField(verbose_name='创建时间', default=datetime.datetime.now)

    def __str__(self):
        return "%s/%s/%s/%s"%(self.user, self.content_object, self.n_goods, self.created_time)

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = verbose_name


class GoodsOrder(models.Model):
    """
    商品订单
    """
    STATUS = (
        (enums.ORDER_PAY_STATUS_COMPLETE, "已支付订单"),
        (enums.ORDER_PAY_STATUS_UN_COMPLETE, "未支付订单"),
        (enums.ORDER_PAY_STATUS_CANCEL, '订单取消')
    )
    TYPES = (
        (enums.PAYMENT_TYPES_ALIPAY, '支付宝'),
        (enums.PAYMENT_TYPES_WEICHAT, '微信')
    )
    user = models.ForeignKey(User, verbose_name='付费用户', on_delete=models.CASCADE)
    order_sn = models.CharField(verbose_name='订单编号', max_length=50, unique=True)
    trade_sn = models.CharField(verbose_name='第三方交易编号', max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(verbose_name='支付状态', choices=STATUS, max_length=20, default=enums.ORDER_PAY_STATUS_UN_COMPLETE)
    order_amount = models.FloatField(verbose_name='订单金额', default=0)
    payment_type = models.CharField(verbose_name="支付方式", choices=TYPES, max_length=20, default=enums.PAYMENT_TYPES_ALIPAY)
    message = models.CharField(verbose_name='订单留言', max_length=255, blank=True, null=True)
    signer = models.ForeignKey(Signer, verbose_name='签收人', on_delete=models.CASCADE)
    address = models.CharField(verbose_name='寄送地址', max_length=300)
    created_time = models.DateTimeField(verbose_name='订单创建时间', default=datetime.datetime.now)

    @classmethod
    def remove_cancelled_order(cls):
        cls.objects.filter(status=enums.ORDER_PAY_STATUS_CANCEL).delete()

    def __str__(self):
        return "%s/%s"%(self.user, self.order_sn)

    class Meta:
        verbose_name = '商品订单信息'
        verbose_name_plural = verbose_name


class GoodsOrderReleation(models.Model):
    """
    订单商品关系
    """
    order = models.ForeignKey(GoodsOrder, verbose_name='关联订单', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, verbose_name='关联商品内容类型', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(verbose_name='关联商品id')
    content_object = GenericForeignKey('content_type', 'object_id')  # 关联商品
    n_goods = models.PositiveIntegerField(verbose_name='商品购买数量', default=0)
    created_time = models.DateTimeField(verbose_name='添加时间', default=datetime.datetime.now)

    def __str__(self):
        return "%s/%s"%(self.order, self.content_object)

    def get_admin_releated_url(self):
        return "%s/%s/%s"%(self._meta.app_label, self._meta.model_name, self.pk)

    class Meta:
        verbose_name = '订单商品关系'
        verbose_name_plural = verbose_name


class PaymentLogs(models.Model):
    """
    商品支付记录
    """
    user = models.ForeignKey(User, verbose_name='付费用户', on_delete=models.CASCADE)
    goods_sn = models.CharField(verbose_name='商品序列号', max_length=50, unique=True)
    goods_order = models.ForeignKey(GoodsOrderReleation, verbose_name='关联订单', on_delete=models.CASCADE)
    created_time = models.DateTimeField(verbose_name='创建时间', default=datetime.datetime.now)

    def __str__(self):
        return "%s/%s"%(self.user, self.goods_sn)

    class Meta:
        verbose_name = '商品支付记录'
        verbose_name_plural = verbose_name