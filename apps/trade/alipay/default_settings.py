#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      default_settings.py 
@time:      2018/08/22 
"""

import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = settings.BASE_DIR

TRADE = {  # 自定义设置
    'alipay': {
        'appid': '2016091700535510',
        'alipay_public_key_path': os.path.join(BASE_DIR, 'apps/trade/alipay/secerts/alipay_public_key.pem'),
        'app_private_key_path': os.path.join(BASE_DIR, 'apps/trade/alipay/secerts/app_private_key.pem'),
        'notify_url': 'http://59.110.222.209:8000/trade/alipay/return/',
        'return_url': 'http://59.110.222.209:8000/trade/alipay/return/',
        'sign_type': "RSA2",
        'debug': True
    }
}

base_settings = getattr(settings, 'TRADE', None)
default_trade_settings = TRADE.copy()

if base_settings:
    if isinstance(base_settings, dict):
        if 'alipay' in base_settings:
            alipay_settings = base_settings['alipay']
            if not isinstance(alipay_settings, dict):
                raise ImproperlyConfigured('TRADE["%s"] setting must be a dictionary type.' % 'alipay')
            default_trade_settings.update(alipay_settings)
        else:
            raise ImproperlyConfigured("No configuration named '%s' found in your TRADE setting." % 'alipay')
    else:
        raise ImproperlyConfigured('TRADE setting must be a dictionary type.')
