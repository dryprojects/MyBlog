#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      views.py 
@time:      2018/07/29 
"""

from rest_framework import viewsets, filters as rest_filters, throttling as rest_throttling, \
    permissions as rest_permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from django.db.models import F
from django.contrib.contenttypes.models import ContentType

from django_filters import rest_framework as filters
from dry_rest_permissions.generics import DRYPermissions
from drf_haystack.viewsets import HaystackViewSet
from drf_haystack import filters as haystack_filters
from drf_haystack import mixins as haystack_mixins

from blog import models, enums
from blog.api import serializers, paginators, permissions, throttling, filters as blog_filters
from oper.models import FriendshipLinks
from trade.models import ShoppingCart


class PostViewset(viewsets.ModelViewSet):
    """
    list:
    返回用户所有公开发表的博文，当前用户返回所有的博文

    retrieve:
    返回的博文如果是收费的则需要对应权限才可访问

    delete:
    只有博文作者才可以

    update:
    只有博文作者才可以
    """
    queryset = models.Post.objects.all()
    pagination_class = paginators.PostPaginator
    permission_classes = (permissions.BlacklistPermission, permissions.DRYPostPermissions)
    throttle_classes = (throttling.PostUserRateThrottle, rest_throttling.AnonRateThrottle)
    filter_backends = (
        filters.DjangoFilterBackend, rest_filters.OrderingFilter, rest_filters.SearchFilter,
        blog_filters.PostFilterBackend)
    filter_class = blog_filters.PostFilter  # 注意这里不是重写 filterset_class 属性
    search_fields = ('title', 'category__name')
    ordering_fields = ('published_time', 'n_praise', 'n_browsers')
    ordering = ('-published_time',)  # 默认排序规则

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return serializers.PostDetailSerializer
        elif self.action in ["update", "partial_update", "create"]:
            return serializers.PostSerializer
        else:
            return serializers.PostListSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        统计博文浏览次数
        """
        p = self.get_object()
        p.n_browsers = F('n_browsers') + 1
        p.save()
        return super().retrieve(request, *args, **kwargs)

    def get_standard_list_response(self, request):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True, context={'request': self.request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context={'request': self.request})
        return Response(serializer.data)

    @action(detail=False)
    def get_notifications(self, request):
        """
        ### list: 返回站点公告
        """
        return self.get_standard_list_response(request)

    @action(detail=False, filter_class=blog_filters.ArchiveFilter)
    def get_archives(self, request):
        """
        list:
        返回博文按照月份的归档

        | 查询参数 | 描述 |

        | ------ | ------ |

        | published_time_year | 返回指定年份的归档 |

        | published_time_month | 返回指定月份的归档 |

        """
        queryset = self.get_queryset()
        query = {
            'status': enums.POST_STATUS_PUBLIC,
            'post_type': enums.POST_TYPE_POST
        }
        queryset = queryset.filter(**query)
        date_queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(date_queryset)
        if page:
            serializer = serializers.PostArchiveSerializer(page, many=True,
                                                           context={'request': self.request, 'queryset': queryset})
            return self.get_paginated_response(serializer.data)
        serializer = serializers.PostArchiveSerializer(date_queryset, many=True,
                                                       context={'request': self.request, 'queryset': queryset})
        return Response(serializer.data)

    @action(detail=False)
    def get_hot_posts(self, request):
        """###list: 返回热门博文"""
        return self.get_standard_list_response(request)

    @action(detail=False)
    def get_max_praise_posts(self, request):
        """###list: 返回点赞最多的博文"""
        return self.get_standard_list_response(request)

    @action(detail=False)
    def get_banners(self, request):
        """###list: 返回需要在轮播展示的博文"""
        return self.get_standard_list_response(request)

    @action(detail=False)
    def get_friendship_links(self, request):
        """
        ###list: 返回站点友情链接
        """
        queryset = FriendshipLinks.objects.all()

        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True, context={'request': self.request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context={'request': self.request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[rest_permissions.IsAuthenticated])
    def set_praise(self, request, pk):
        """GET: 点赞博文"""
        self.object = self.get_object()
        self.object.n_praise = F('n_praise') + 1
        self.object.save()
        self.object.refresh_from_db()

        serializer = serializers.PostPraiseSerializer({'detail': self.object.n_praise})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[rest_permissions.IsAuthenticated])
    def set_favorite(self, request, pk):
        """GET: 收藏博文"""
        content_type = ContentType.objects.get_for_model(models.Post)
        checked = request.user.favorite(content_type, pk)
        res = {'status': 'success', "detail": "收藏成功"} if checked else {'status': 'failed', "detail": '你已经收藏过这篇博文'}
        serializer = serializers.PostFavoriteSerializer(res)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[rest_permissions.IsAuthenticated])
    def cancel_favorite(self, request, pk):
        """GET: 取消收藏博文"""
        content_type = ContentType.objects.get_for_model(models.Post)
        checked = request.user.cancel_favorite(content_type, pk)
        res = {'status': 'success', "detail": "取消收藏成功"} if checked else {'status': 'failed', "detail": '你还没有收藏此博文'}
        serializer = serializers.PostFavoriteSerializer(res)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'delete'], permission_classes=[rest_permissions.IsAuthenticated])
    def add_to_shoppingcart(self, request, pk):
        """将博文添加到购物车,或者对购物车中的博文数量减一"""
        content_type = ContentType.objects.get_for_model(models.Post)
        incr = False if request.method in ['DELETE'] else True
        res = ShoppingCart.add_item(content_type, pk, request.user, incr)

        if not res.success:
            return Response({'detail': res.detail}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': res.detail}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[rest_permissions.IsAuthenticated])
    def del_from_shoppingcart(self, request, pk):
        """将博文移出购物车"""
        content_type = ContentType.objects.get_for_model(models.Post)
        res = ShoppingCart.del_item(content_type, pk, request.user)

        if not res.success:
            return Response({'detail': res.detail}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': res.detail}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[rest_permissions.IsAuthenticated])
    def get_content_type(self, request):
        """list: 返回博文的内容类型id"""
        content_type = ContentType.objects.get_for_model(models.Post)
        serializer = serializers.ContentTypeSerializer(content_type)
        return Response(serializer.data)


class PostSearchViewSet(haystack_mixins.MoreLikeThisMixin, haystack_mixins.FacetMixin, HaystackViewSet):
    """
    list:
    返回所有被索引的文档，可以通过查询参数进行全文搜索 例：?text=python 将会搜索出所有关于python的文档

    more-like-this:
    返回相似的文档

    facets:
    返回在作者和博文发表日期上分面搜索（垂直搜索，分片搜索）的结果， [相关概念][ref]
    [ref]: https://django-haystack.readthedocs.io/en/latest/faceting.html
    """
    # 这里默认是id，但是文档(这个文档指的是搜索索引里的文档)里默认是django_id,酌情更改 ^_^
    # 相关配置 HAYSTACK_DJANGO_ID_FIELD
    # see https://django-haystack.readthedocs.io/en/latest/settings.html?highlight=HAYSTACK_DJANGO_ID_FIELD%20#haystack-django-id-field
    document_uid_field = 'django_id'
    index_models = [models.Post]
    serializer_class = serializers.PostSearchSerializer
    facet_serializer_class = serializers.PostFacetSerializer
    filter_backends = [haystack_filters.HaystackHighlightFilter]


class PostAutocompleteSearchViewSet(HaystackViewSet):
    """
    list:
    返回所有可用的建议

    查询参数： ?q=mysql 返回mysql的建议
    """
    index_models = [models.Post]
    serializer_class = serializers.PostAutocompleteSerializer
    filter_backends = [haystack_filters.HaystackAutocompleteFilter]


class CategoryViewset(viewsets.ModelViewSet):
    """
    read : 返回当前登录用户的所有分类
    write: 只有分类的作者可以删除分类
    """
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategoryTreeSerializer
    permission_classes = (DRYPermissions,)
    filter_backends = (blog_filters.CategoryFilterBackend, filters.DjangoFilterBackend)
    filter_class = blog_filters.CategoryFilter


class TagViewset(viewsets.ModelViewSet):
    """
    read: 返回当前登录用户的所有标签
    write： 只有标签作者可以进行删除，更新
    """
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagDetailSerializer
    permission_classes = (DRYPermissions,)
    filter_backends = (blog_filters.TagFilterBackend, filters.DjangoFilterBackend)
    filter_class = blog_filters.TagFilter


class ResourceViewset(viewsets.ModelViewSet):
    """
    read: 返回当前登录用户的所有博文资源
    write： 只有标签作者可以进行删除，更新
    """
    queryset = models.Resources.objects.all()
    serializer_class = serializers.ResourceSerializer
    permission_classes = (DRYPermissions,)
    filter_backends = (blog_filters.PostResourceBackend, filters.DjangoFilterBackend)
    filter_class = blog_filters.PostResourceFilter
