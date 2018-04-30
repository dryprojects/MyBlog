# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/31 15:05'

from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget

# see detail
# http://kindeditor.net/docs/usage.html
# http://kindeditor.net/docs/option.html

class KindTextareaWidget(forms.Textarea):
    template_name = 'kindeditor/editor.html'

    def __init__(self, attrs=None, config=None):
        self.config = config or {
            "height":"300px",
            "width":"690px"
        }

        super(KindTextareaWidget, self).__init__(attrs) #for python2.7

    @property
    def media(self):
        css = {
            'all': ('kindeditor/plugins/code/prettify.css',)
        }
        js = [
            'kindeditor/kindeditor-all-min.js',
            'kindeditor/lang/zh-CN.js',
            'kindeditor/plugins/code/prettify.js'
        ]
        return forms.Media(js=js, css=css)

    def get_context(self, name, value, attrs):
        context = super(KindTextareaWidget, self).get_context(name, value, attrs)
        widget = context['widget']
        widget["config"] = self.config
        return context