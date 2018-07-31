#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      permissions.py 
@time:      2018/07/30 
"""

from django.conf import settings

from rest_framework import permissions
from ipware import get_client_ip

from oper.models import Blacklist


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            # Check permissions for read-only request
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.author == request.user


class BlacklistPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    run against all incoming requests
    """

    def has_permission(self, request, view):
        client_ip, is_routable = get_client_ip(request)
        if client_ip is None:
            # Unable to get the client's IP address
            return True
        else:
            # We got the client's IP address
            if is_routable:
                # The client's IP address is publicly routable on the Internet
                blacklisted = Blacklist.objects.filter(ip_addr=client_ip).exists()
            else:
                # The client's IP address is private
                return True

        # Order of precedence is (Public, Private, Loopback, None)
        return not blacklisted


class ReadPermission(permissions.DjangoObjectPermissions):
    """
    对象读取权限控制
    """
    message = '你没有权限访问， 请向管理员申请'
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
    }

    def has_permission(self, request, view):
        """
        全局权限检测
        这里不做模型权限检测，默认具有访问对应模型的权限
        :param request:
        :param view:
        :return:
        """

        if not request.user or not request.user.is_authenticated:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        检查用户是否对访问的博文实例具有读取权限 view_post
        :param request:
        :param view:
        :param obj:
        :return:
        """
        queryset = self._queryset(view)
        model_cls = queryset.model
        user = request.user

        perms = self.get_required_object_permissions(request.method, model_cls)

        if not user.has_perms(perms, obj):
            return False

        return True