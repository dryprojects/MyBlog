#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      mixins.py 
@time:      2018/05/05 
"""

from django.contrib.auth.views import SuccessURLAllowedHostsMixin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.conf import settings


class RedirectMixin(SuccessURLAllowedHostsMixin):
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or resolve_url(settings.REGISTER_REDIRECT_URL)

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''
