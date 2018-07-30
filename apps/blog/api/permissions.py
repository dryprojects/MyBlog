#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      permissions.py 
@time:      2018/07/30 
"""

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
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }