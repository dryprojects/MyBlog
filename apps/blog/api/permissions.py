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
from dry_rest_permissions.generics import DRYPermissions

from oper.models import Blacklist


class DRYPostPermissions(DRYPermissions):
    message = "你无权访问，请向作者申请访问权限"


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
        return (obj.author == request.user) or request.user.is_superuser


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
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False

        is_owner_or_root = (obj.author == request.user) or request.user.is_superuser

        return True if is_owner_or_root else self.check_view_perm(request, view, obj)

    def check_view_perm(self, request, view, obj):
        has_view_perm = False # 不是所有者的只有具有访问权限才可以访问

        queryset = self._queryset(view)
        model_cls = queryset.model
        user = request.user

        perms = self.get_required_object_permissions(request.method, model_cls)
        if user.has_perms(perms, obj):
            has_view_perm = True

        return has_view_perm



class BlacklistPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    run against all incoming requests
    """

    message = "你被暂时列入访问黑名单了。"

    def has_permission(self, request, view):
        client_ip, is_routable = get_client_ip(request)
        if client_ip is None:
            # Unable to get the client's IP address
            return False
        else:
            # We got the client's IP address
            if is_routable:
                # The client's IP address is publicly routable on the Internet
                blacklisted = self.check_blacklist(client_ip)
            else:
                # The client's IP address is private
                blacklisted = self.check_blacklist(client_ip)

        # Order of precedence is (Public, Private, Loopback, None)
        return not blacklisted

    def check_blacklist(self, ip_addr):
        #首先删除过期的ip
        Blacklist.remove_expired()

        blacklisted = Blacklist.objects.filter(ip_addr=ip_addr).exists()
        if blacklisted:
            client = Blacklist.objects.filter(ip_addr=ip_addr).first()
            if client.desc:
                self.message = client.desc

        return blacklisted