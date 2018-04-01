# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/31 17:28'

import json

from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.filter(name='convert_to_json', is_safe=True)
def convert(config:dict) -> json:
    """
    convert the dict config to json
    :param config:
    :return: json
    """
    c = json.dumps("{}")
    try:
        c = json.dumps(config)
    except:
        pass
    return mark_safe(c)