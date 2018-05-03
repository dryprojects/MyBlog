# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/31 15:05'

from django import forms


# see detail
# http://kindeditor.net/docs/usage.html
# http://kindeditor.net/docs/option.html

class KindTextareaWidget(forms.Textarea):
    template_name = 'kindeditor/editor.html'

    def __init__(self, attrs=None, config=None):
        self.config = config or {
            "height": "300px",
            "width": "800px"
        }

        self.config.update({
            "items": [
                'emoticons', 'image', 'paste', 'plainpaste', 'wordpaste', '|', 'justifyleft', 'justifycenter',
                'justifyright',
                'justifyfull', 'insertorderedlist', 'insertunorderedlist', 'formatblock', 'fontname', 'fontsize', '|',
                'forecolor', 'bold',
                'italic', 'underline', 'lineheight', '|', 'link', 'unlink', 'fullscreen'
            ],
            "filterMode": False,
            "uploadJson": '/kindeditor/upload/'
        })

        super(KindTextareaWidget, self).__init__(attrs)  # for python2.7

    @property
    def media(self):
        js = [
            'kindeditor/kindeditor-all.js',
            'kindeditor/lang/zh-CN.js',
        ]
        return forms.Media(js=js)

    def get_context(self, name, value, attrs):
        context = super(KindTextareaWidget, self).get_context(name, value, attrs)
        widget = context['widget']
        widget["config"] = self.config
        return context
