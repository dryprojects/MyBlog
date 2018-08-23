import datetime
import collections

from django.db import models
from django.db.models import F
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.db.transaction import atomic, savepoint, savepoint_commit, savepoint_rollback, clean_savepoints

from trade import enums

# Create your models here.
User = get_user_model()


class ShoppingCart(models.Model):
    """
    购物车
    """
    user = models.ForeignKey(User, verbose_name='付费用户', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, verbose_name='商品类型', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(verbose_name='商品id')
    content_object = GenericForeignKey('content_type', 'object_id')  # 商品实体
    n_goods = models.PositiveIntegerField(verbose_name='商品购买数量', default=1)
    created_time = models.DateTimeField(verbose_name='创建时间', default=datetime.datetime.now)

    def __str__(self):
        return "%s/%s/%s/%s" % (self.user, self.content_object, self.n_goods, self.created_time)

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = verbose_name

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    @classmethod
    def add_item(cls, content_type, pk, user, incr=True):
        """
        将指定商品添加到购物车
        :param content_type: 商品类型
        :param pk: 商品id
        :param user: 购物车所属用户
        :return:
        """
        qs = cls.objects.filter(content_type=content_type, object_id=pk, user=user)
        Result = collections.namedtuple('Result', ['success', 'detail'])

        with atomic():
            if qs.exists():
                # 如果购物车里有相同的商品，则对商品数量+1/-1
                qs.update(n_goods=F('n_goods') + 1) if incr else qs.update(n_goods=F('n_goods') - 1)
                return Result(True, qs.first().n_goods)

            cls.objects.create(content_type=content_type, object_id=pk, user=user)

        return Result(True, qs.first().n_goods)

    @classmethod
    def del_item(cls, content_type, pk, user):
        """
        清除购物车条目
        :param content_type:
        :param pk:
        :param user:
        :return:
        """
        qs = cls.objects.filter(content_type=content_type, object_id=pk, user=user)
        Result = collections.namedtuple('Result', ['success', 'detail'])

        with atomic():
            if qs.exists():
                qs.delete()

                return Result(True, "已移出购物车")

        return Result(True, "已移出购物车")

    @classmethod
    def clear_shoppingcart(cls, user):
        """
        清空用户购物车
        :param user:
        :return:
        """
        Result = collections.namedtuple('Result', ['success', 'detail'])

        cls.objects.filter(user=user).delete()

        return Result(True, '已清空购物车')


class GoodsOrder(models.Model):
    """
    商品订单
    """
    STATUS = (
        (enums.ORDER_PAY_STATUS_COMPLETE, "已支付订单"),
        (enums.ORDER_PAY_STATUS_UN_COMPLETE, "未支付订单"),
        (enums.ORDER_PAY_STATUS_CANCEL, '订单取消'),
        # alipay
        ('WAIT_BUYER_PAY', '交易创建，等待买家付款'),
        ('TRADE_CLOSED', '未付款交易超时关闭，或支付完成后全额退款'),
        ('TRADE_SUCCESS', '交易支付成功'),
        ('TRADE_FINISHED', '交易结束，不可退款')
    )
    TYPES = (
        (enums.PAYMENT_TYPES_ALIPAY, '支付宝'),
        (enums.PAYMENT_TYPES_WEICHAT, '微信')
    )
    user = models.ForeignKey(User, verbose_name='付费用户', on_delete=models.CASCADE)
    order_sn = models.CharField(verbose_name='订单编号', max_length=50, unique=True, null=True, blank=True)
    trade_sn = models.CharField(verbose_name='第三方交易编号', max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(verbose_name='支付状态', choices=STATUS, max_length=20,
                              default='WAIT_BUYER_PAY')
    order_amount = models.FloatField(verbose_name='订单金额', default=0)
    payment_type = models.CharField(verbose_name="支付方式", choices=TYPES, max_length=20,
                                    default=enums.PAYMENT_TYPES_ALIPAY)
    pay_time = models.DateTimeField(verbose_name='支付时间', null=True, blank=True)
    message = models.CharField(verbose_name='订单留言', max_length=255, blank=True, null=True)
    signer_name = models.CharField(verbose_name='签收人称呼', max_length=30)
    signer_phone_num = models.CharField(verbose_name='联系电话', max_length=14)
    sign_time = models.DateTimeField(verbose_name='签收时间', null=True, blank=True)
    address = models.CharField(verbose_name='寄送地址', max_length=300)
    created_time = models.DateTimeField(verbose_name='订单创建时间', default=datetime.datetime.now)

    @classmethod
    def remove_cancelled_order(cls):
        cls.objects.filter(status=enums.ORDER_PAY_STATUS_CANCEL).delete()

    @classmethod
    def checkout_order(cls):
        """
        结算订单
        :return:
        """

    def __str__(self):
        return "%s/%s" % (self.user, self.order_sn)

    class Meta:
        verbose_name = '商品订单信息'
        verbose_name_plural = verbose_name

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        return request.user == self.user


class GoodsOrderReleation(models.Model):
    """
    订单商品关系
    """
    order = models.ForeignKey(GoodsOrder, verbose_name='关联订单', on_delete=models.CASCADE, related_name='goods_list')
    content_type = models.ForeignKey(ContentType, verbose_name='关联商品内容类型', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(verbose_name='关联商品id')
    content_object = GenericForeignKey('content_type', 'object_id')  # 关联商品
    n_goods = models.PositiveIntegerField(verbose_name='商品购买数量', default=0)
    created_time = models.DateTimeField(verbose_name='添加时间', default=datetime.datetime.now)

    def __str__(self):
        return "%s/%s" % (self.order, self.content_object)

    def get_admin_releated_url(self):
        return "%s/%s/%s" % (self._meta.app_label, self._meta.model_name, self.pk)

    class Meta:
        verbose_name = '订单商品关系'
        verbose_name_plural = verbose_name

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        return request.user == self.order.user



class PaymentLogs(models.Model):
    """
    商品支付记录
    """
    user = models.ForeignKey(User, verbose_name='付费用户', on_delete=models.CASCADE)
    goods_sn = models.CharField(verbose_name='商品序列号', max_length=50, unique=True)
    goods_order = models.ForeignKey(GoodsOrder, verbose_name='关联订单', on_delete=models.CASCADE)
    created_time = models.DateTimeField(verbose_name='创建时间', default=datetime.datetime.now)

    def __str__(self):
        return "%s/%s" % (self.user, self.goods_sn)

    class Meta:
        verbose_name = '商品支付记录'
        verbose_name_plural = verbose_name
