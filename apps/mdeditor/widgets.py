#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      widgets.py 
@time:      2018/05/01 
"""

from django import forms
from django.conf import settings
from django.forms.utils import flatatt
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


DEFAULT_CONFIG = {
    'toolbar': ["undo", "redo", "|", "bold", "del", "italic", "quote", "ucwords", "uppercase", "lowercase", "|",
                "h1", "h2", "h3", "h5", "h6", "|", "list-ul", "list-ol", "hr", "|","link", "reference-link", "image",
                "code", "preformatted-text", "code-block", "table", "datetime", "emoji", "html-entities", "pagebreak",
                "goto-line", "|", "||", "preview", "watch", "fullscreen"
                ],
    'upload_image_formats': ["jpg", "jpeg", "gif", "png", "bmp", "webp"],
    'image_floder': 'mdeditor',
    'theme': 'default',  # dark / default
    'preview_theme': 'default',  # dark / default
    'editor_theme': 'default',  # pastel-on-dark / default
    'toolbar_autofixed': True,
    'search_replace': True,
    'emoji': True,
    'tex': True,
    'flow_chart': True,
    'sequence': True,
    'tocm':True
}


class MdTextWidget(forms.Textarea):
    template_name = 'mdeditor/editor.html'

    def __init__(self, config_name='default', *args, **kwargs):
        self.config = DEFAULT_CONFIG.copy()

        configs = getattr(settings, 'MDEDITOR_CONFIGS', None)

        if configs:
            if isinstance(configs, dict):
                # Make sure the config_name exists.
                if config_name in configs:
                    config = configs[config_name]
                    # Make sure the configuration is a dictionary.
                    if not isinstance(config, dict):
                        raise ImproperlyConfigured('MDEDITOR_CONFIGS["%s"] \
                                        setting must be a dictionary type.' %
                                                   config_name)
                    # Override defaults with settings config.
                    self.config.update(config)
                else:
                    raise ImproperlyConfigured("No configuration named '%s' \
                                    found in your MDEDITOR_CONFIGS setting." %
                                               config_name)
            else:
                raise ImproperlyConfigured('MDEDITOR_CONFIGS setting must be a\
                                dictionary type.')

        super(MdTextWidget, self).__init__(*args, **kwargs)

    @property
    def media(self):
        css = {
            'all': ('mdeditor/css/editormd.min.css',
                    'mdeditor/css/editormd.preview.css',
                    'mdeditor/css/custom.css',
                    )
        }
        js = [
            'mdeditor/jquery.min.js',
            'mdeditor/editormd.min.js',
        ]
        return forms.Media(js=js, css=css)

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''

        final_attrs = self.build_attrs(self.attrs, attrs, name=name)
        return mark_safe(render_to_string(self.template_name, {
            'final_attrs': flatatt(final_attrs),
            'value': conditional_escape(force_text(value)),
            'id': final_attrs['id'],
            'config': self.config,
        }))

    def build_attrs(self, base_attrs, extra_attrs=None, **kwargs):
        attrs = dict(base_attrs, **kwargs)
        if extra_attrs:
            attrs.update(extra_attrs)
        return attrs