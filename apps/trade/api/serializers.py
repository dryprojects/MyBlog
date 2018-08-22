#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      serializers.py 
@time:      2018/08/16 
"""

from rest_framework import serializers

from generic_relations.relations import GenericRelatedField, GenericSerializerMixin
from drf_writable_nested.mixins import NestedCreateMixin

from trade import models
from trade.alipay import client as alipay_client, settings as alipay_settings
from blog import models as blog_models
from blog.api import serializers as blog_serializers


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    content_object = GenericRelatedField({
        blog_models.Post: blog_serializers.PostListSerializer()
    })

    class Meta:
        model = models.ShoppingCart
        fields = ('user', 'content_object', 'n_goods', 'created_time')


class GoodsOrderDetailSerializer(serializers.ModelSerializer):
    content_object = GenericRelatedField({
        blog_models.Post: blog_serializers.PostListSerializer()
    })

    class Meta:
        model = models.GoodsOrderReleation
        fields = (
            'content_object',
            'n_goods',
            'created_time',
        )


class GoodsOrderListSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    goods_list = GoodsOrderDetailSerializer(many=True, read_only=True)
    purchase_link = serializers.SerializerMethodField()

    def get_purchase_link(self, obj):
        query_string = alipay_client.api_alipay_trade_page_pay(
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_amount,
            return_url=alipay_settings['return_url']
        )
        if alipay_settings['debug']:
            url = 'https://openapi.alipaydev.com/gateway.do?{query_string}'.format(query_string=query_string)
        else:
            url = "https://openapi.alipay.com/gateway.do?{query_string}".format(query_string=query_string)

        return url

    class Meta:
        model = models.GoodsOrder
        fields = (
            'id',
            'user',
            'order_sn',
            'trade_sn',
            'status',
            'order_amount',
            'payment_type',
            'pay_time',
            'message',
            'address',
            'signer_name',
            'signer_phone_num',
            'sign_time',
            'created_time',
            'goods_list',
            'purchase_link'
        )

        read_only_fields = (
            'order_sn',
            'trade_sn',
            'status',
            'created_time',
            'sign_time',
            'pay_time'
        )

    def create(self, validated_data):
        """
        根据用户的购物车生成订单商品关系
        :param validated_data:
        :return:
        """
        goods_order = super().create(validated_data)
        shopping_cart_goods_list = models.ShoppingCart.objects.filter(user=self.context['request'].user)
        for item in shopping_cart_goods_list:
            models.GoodsOrderReleation.objects.create(
                content_type=item.content_type,
                object_id=item.object_id,
                n_goods=item.n_goods,
                order=goods_order,
            )
        # 生成订单后清空用户购物车
        models.ShoppingCart.clear_shoppingcart(self.context['request'].user)

        return goods_order