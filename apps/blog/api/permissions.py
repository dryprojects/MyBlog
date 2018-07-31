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

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            # Check permissions for read-only request
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.author == request.user


class IsOwnerOrNeedAccess(permissions.DjangoObjectPermissions):
    """
        让实例所有者具有实例的所有权限，
        而访问者，只有在实例上具有可访问权限时才能访问对应实例
    """
    message = '你无权访问，请向所有者申请访问权限。'
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
    }

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False  # 匿名用户不可访问

        if request.method not in ["DELETE", "PUT", "PATCH"]:
            return True

        return view.get_object().author == request.user #删除，更新，只有所有者才可以操作

    def has_object_permission(self, request, view, obj):
        if obj.author == request.user:
            return True

        queryset = self._queryset(view)
        model_cls = queryset.model
        user = request.user

        perms = self.get_required_object_permissions(request.method, model_cls)
        if request.method in permissions.SAFE_METHODS:
            if not user.has_perms(perms, obj):
                return False
            return True  # 不是所有者的只有具有访问权限才可以访问

        return False


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
