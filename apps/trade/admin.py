from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from trade.models import PaymentLogs, GoodsOrderReleation, GoodsOrder, ShoppingCart


@admin.register(ShoppingCart)
class ShoppingCartModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_object', 'n_goods', 'created_time']
    fieldsets = (
        ("基本信息", {
            "fields": [('user', "content_type", 'object_id'), ("n_goods", 'created_time')],
            'classes': ('extrapretty',)
        }),
    )
    autocomplete_fields = ['user']

    def content_object(self, instance):
        if hasattr(instance.content_object, 'get_absolute_url'):
            return format_html("<a href='{}'>{}</a>", instance.content_object.get_absolute_url(), instance.content_object)
        return instance.content_object
    content_object.short_description = '付费商品'


class GoodsOrderReleationInline(admin.TabularInline):
    model = GoodsOrderReleation
    extra = 1


@admin.register(GoodsOrder)
class GoodsOrderModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    search_fields = ["order_sn"]
    list_display = ['order_sn', 'trade_sn', 'user', 'order_amount', 'payment_type', 'status', 'signer_name', 'signer_phone_num', 'sign_time', 'created_time']
    fieldsets = (
        ("基本信息", {
            "fields": [('order_sn', "trade_sn", 'user'), ("order_amount", 'payment_type', 'status'), ("message", 'signer_name', 'signer_phone_num', 'sign_time', "address"), 'created_time'],
            'classes': ('extrapretty',)
        }),
    )

    inlines = [GoodsOrderReleationInline]


@admin.register(GoodsOrderReleation)
class GoodsOrderReleationModelAdmin(admin.ModelAdmin):
    search_fields = ['order']
    autocomplete_fields = ['order']
    list_display = ['order', 'content_object', 'created_time']
    fieldsets = (
        ('记录', {
            'fields': [('order', 'n_goods'), ('content_type', 'object_id', 'created_time')],
            'classes': ('extrapretty',)
        }),
    )
    def content_object(self, instance):
        if hasattr(instance.content_object, 'get_absolute_url'):
            return format_html("<a href='{}'>{}</a>", instance.content_object.get_absolute_url(), instance.content_object)
        return instance.content_object
    content_object.short_description = '付费商品'


@admin.register(PaymentLogs)
class PaymentLogsModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'goods_sn', 'goods_orders', 'created_time')
    autocomplete_fields = ['user', 'goods_order']
    fieldsets = (
        ('记录', {
            'fields': [('user', 'goods_sn'), ('goods_order', 'created_time')],
            'classes': ('extrapretty',)
        }),
    )

    def goods_orders(self, instance):
        if hasattr(instance.goods_order, 'get_admin_releated_url'):
            return format_html("<a href='/admin/{}'>{}</a>", instance.goods_order.get_admin_releated_url(), instance.goods_order)
        return instance.goods_order

    goods_orders.short_description = '关联商品订单'