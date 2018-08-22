#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      views.py 
@time:      2018/08/21 
"""
import datetime

from rest_framework import mixins, viewsets, views, response

from alipay import AliPay

from trade.alipay import client
from trade import models


class AlipayAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
        """
        处理alipay同步返回结果
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return self.get_trade_response(request.GET, async=False)

    def post(self, request, *args, **kwargs):
        """
        处理alipay异步返回结果
        see https://docs.open.alipay.com/270/105902/
        例：
            'gmt_create':'2018-08-22 14:00:27'
            'charset':'utf-8'
            'gmt_payment':'2018-08-22 14:00:34'
            'notify_time':'2018-08-22 14:00:35'
            'subject':'测试订单'
            'sign':''
            'buyer_id':'2088102176484614'
            'invoice_amount':'100.00'
            'version':'1.0'
            'notify_id':'5a6c616df3fc5848b10b89ef591c996kpi'
            'fund_bill_list':'[{"amount":"100.00","fundChannel":"ALIPAYACCOUNT"}]'
            'notify_type':'trade_status_sync'
            'out_trade_no':'201702012356'
            'total_amount':'100.00'
            'trade_status':'TRADE_SUCCESS'
            'trade_no':'2018082221001004610200685330'
            'auth_app_id':'2016091700535510'
            'receipt_amount':'100.00'
            'point_amount':'0.00'
            'app_id':'2016091700535510'
            'buyer_pay_amount':'100.00'
            'sign_type':'RSA2'
            'seller_id':'2088102176098198'
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return self.get_trade_response(request.POST)

    def get_trade_response(self, data, async=True):
        res_dict = {k: v for k, v in data.items()}
        signature = res_dict.pop("sign", None)
        if signature:
            success = client.verify(res_dict, signature)
            if success:
                order_sn = res_dict.get('out_trade_no', None)
                trade_sn = res_dict.get('trade_no', None)

                if async:
                    # 修改客户订单状态
                    trade_status = res_dict.get('trade_status', None)
                    models.GoodsOrder.objects.filter(order_sn=order_sn).update(status=trade_status, trade_sn=trade_sn,
                                                                               pay_time=datetime.datetime.now())

                    return response.Response("success")
                else:
                    #return_url检测订单状态
                    order = models.GoodsOrder.objects.get(order_sn=order_sn)
                    #这里可以重定向到支付结果的页面，显示订单的支付状态
                    return response.Response({'status': order.get_status_display()})

        return response.Response('failure')
