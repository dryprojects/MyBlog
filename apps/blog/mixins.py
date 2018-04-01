# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/27 19:05'

from django.http import JsonResponse


class JSONResponseMixin:
    """
    a mixin that can be used to render a JSON response
    """
    def render_to_response(self, context, **response_kwargs):
        """

        :param context:
        :param response_kwargs:
        :return:
        """
        return JsonResponse(self.get_data(context), **response_kwargs)

    def get_data(self, context):
        """
        returns an object that will be serialized  as Json by json.dumps()
        :param context:
        :return:
        """
        return context