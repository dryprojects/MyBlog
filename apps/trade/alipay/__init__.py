#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      __init__.py.py 
@time:      2018/08/20 
""" 

from trade.alipay.default_settings import default_trade_settings
from alipay import AliPay


settings = default_trade_settings['alipay']
client = AliPay(
            appid=settings['appid'],
            app_notify_url=settings['notify_url'],
            app_private_key_string=open(settings['app_private_key_path']).read(),
            alipay_public_key_string=open(settings['alipay_public_key_path']).read(),
            sign_type=settings['sign_type'],
            debug=settings['debug']
        )

if __name__ == '__main__':
    import os
    from urllib.parse import parse_qs, urlparse

    from alipay import AliPay


    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    alipay = AliPay(
        appid="2016091700535510",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=open(
            os.path.join(BASE_DIR, 'apps', 'trade', 'alipay', 'secerts', 'app_private_key.pem')).read(),
        alipay_public_key_string=open(
            os.path.join(BASE_DIR, 'apps', 'trade', 'alipay', 'secerts', 'alipay_public_key.pem')).read(),
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    query_string = alipay.api_alipay_trade_page_pay(
        subject="测试订单",
        out_trade_no="201702012356",
        total_amount=100,
        notify_url='http://59.110.222.209:8000/trade/alipay/return/',  #需要线上地址进行远程调试
        return_url='http://59.110.222.209:8000/trade/alipay/return/'   #可以线下调试
    )

    url = 'https://openapi.alipaydev.com/gateway.do?{query_string}'.format(query_string=query_string)

    print(url)

    #同步返回结果 nhksoq0498@sandbox.com 744194 59.110.222.209
    return_url = 'http://localhost:8000/?charset=utf-8&out_trade_no=2017020103&method=alipay.trade.page.pay.return&total_amount=100.00&sign=JGdIJwsBbpLYBSOMPQVxkqcMuHTw6oiccjynzJPJfsn%2FopP%2Bs78%2Bd%2BAAZWbctNt1DgnrWgkXaB4dcGcCGhxwNgxY4bWZxVjHsQY79XsooMIMp336MDgl2sS0obbvxmZ64UF3LbmaAiMEZAWkhuBxLXEdTF6G7S%2Fu1vQEpPNJ%2Bbz2V1bH7lgXRQQAHIMrF4%2BRfOMLDzfQgiNdsKBj3BsXj0zkLp%2BIUurzj2znCmRdo1Ml1C5lIGg60WzAjJ9sWv1yoFvip6WGJdr1Wcq0rAnSufi6wNsfcSipkWIzE0LGuUmtKM%2FDXnF7wq1WPBZS%2FtydDKQ0sFsk%2Fog6rQPJOyLWGg%3D%3D&trade_no=2018082121001004610200684938&auth_app_id=2016091700535510&version=1.0&app_id=2016091700535510&sign_type=RSA2&seller_id=2088102176098198&timestamp=2018-08-21+19%3A39%3A12'
    query_dict = parse_qs(urlparse(return_url).query)
    query_dict = dict(zip(query_dict, map(lambda _: _[0], query_dict.values()))) #将query_dict中list类型的值，取出变成str类型的值
    signature = query_dict.pop("sign")
    success = alipay.verify(query_dict, signature)

    if success:
        print("trade succeed")

