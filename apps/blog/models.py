import datetime
import hashlib

from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import transaction
from django.conf import settings

from mptt.models import MPTTModel, TreeForeignKey
from mptt.utils import previous_current_next
from dry_rest_permissions.generics import allow_staff_or_superuser, authenticated_users

from comment.models import Comment
from blog import enums
from trade.models import GoodsOrder

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(verbose_name='标签名称', max_length=20, unique=True)
    author = models.ForeignKey(User, verbose_name="作者", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = '博文标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):
        return True

    @authenticated_users
    def has_object_write_permission(self, request):
        """只有作者才能更新和删除对应标签"""
        return request.user == self.author


class Category(MPTTModel):
    name = models.CharField(verbose_name='类目名称', max_length=20, unique=True)
    parent = TreeForeignKey('self', related_name='children', db_index=True, on_delete=models.SET_NULL, null=True,
                            blank=True)
    author = models.ForeignKey(User, verbose_name="作者", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "博文类目"
        verbose_name_plural = verbose_name

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        """只有作者才能更新和删除对应分类"""
        return request.user == self.author


class Post(MPTTModel):
    STATUS = (
        (enums.POST_STATUS_PRIVATE, "私有"),
        (enums.POST_STATUS_PUBLIC, "公开")
    )
    TYPES = (
        (enums.POST_TYPE_POST, '博文'),
        (enums.POST_TYPE_NOTIFICATION, '公告')
    )
    parent = TreeForeignKey('self', verbose_name='上一篇博文', related_name='children', db_index=True,
                            on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(verbose_name='博文标题', max_length=50, help_text="少于50字符")
    cover = models.ImageField(verbose_name='博文封面', upload_to='blog/blog_cover/', max_length=200,
                              default='blog/blog_cover/default.jpg')
    cover_url = models.CharField(verbose_name="博文封面url", max_length=255, null=True, blank=True,
                                 help_text="不写默认为默认封面url")
    category = models.ForeignKey(Category, verbose_name="博文类目", on_delete=models.CASCADE, null=True)  # n ~ 1
    tags = models.ManyToManyField(Tag, verbose_name="博文标签")  # m ~ n
    author = models.ForeignKey(User, verbose_name="博文作者", on_delete=models.CASCADE, null=True)  # n ~ 1
    excerpt = models.TextField(verbose_name="博文摘要", blank=True)
    content = models.TextField(verbose_name='博文内容')
    status = models.CharField(verbose_name="编辑状态", choices=STATUS, max_length=10, default=enums.POST_STATUS_PRIVATE)
    n_praise = models.PositiveIntegerField(verbose_name="点赞数量", default=0)
    n_browsers = models.PositiveIntegerField(verbose_name="浏览次数", default=0)
    published_time = models.DateTimeField(verbose_name="发表时间", default=datetime.datetime.now)
    comments = GenericRelation(Comment, related_query_name='post')
    post_type = models.CharField(verbose_name="博文类型", choices=TYPES, max_length=13, default=enums.POST_TYPE_POST)
    is_banner = models.BooleanField(verbose_name='是否轮播', default=False)
    is_free = models.BooleanField(verbose_name='是否免费', default=True)
    hasbe_indexed = models.BooleanField(verbose_name="已被索引", default=False)
    origin_post_url = models.URLField(verbose_name='原博文URL链接', default="", null=True, blank=True)
    origin_post_from = models.CharField(verbose_name="原博文出处名称", max_length=255, default="", null=True, blank=True)
    url_object_id = models.CharField(verbose_name="源博文唯一标识", unique=True, max_length=255, null=True, blank=True,
                                     help_text="不写默认为博文url摘要")
    post_sn = models.CharField(verbose_name="博文序列号", max_length=50, unique=True)

    class Meta:
        verbose_name = '博文'
        verbose_name_plural = verbose_name

        permissions = (
            ('view_post', "可以查看博文"),
        )

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title

    def was_published_recently(self):
        now = datetime.datetime.now()
        return now - datetime.timedelta(days=1) <= self.published_time <= now

    was_published_recently.admin_order_field = 'published_time'
    was_published_recently.boolean = True
    was_published_recently.short_description = '是否最近发表'

    def get_absolute_url(self):
        return reverse('blog:post-detail', kwargs={'pk': self.pk})

    @property
    def n_comments(self):
        """
        获取该博文的所有评论个数
        :return:
        """
        root_count = 0
        sub_count = 0

        with transaction.atomic():
            # 这里的comments都是content_type为Post的评论，（根评论）
            for comment in self.comments.all():
                if comment:
                    root_count += 1
                    sub_count += comment.n_sub_comment

        return root_count + sub_count

    @property
    def n_comment_users(self):
        """
        该博文评论用户的参与人数
        :return:
        """
        user_set = set()
        with transaction.atomic():
            for root_comment in self.comments.all():
                if root_comment:
                    for sub_comment in root_comment.get_descendants(include_self=True).all():
                        user_set.add(sub_comment.author.username)

        return len(user_set)

    @property
    def prev_this_next(self):
        """
        返回上一篇博文， 当前博文， 下一篇博文的元组
        如果上一篇或者下一篇不存在， 元组对应位置返回 None
        :return: tuple
        """
        queryset = self.get_root().get_descendants(include_self=True)
        for t in previous_current_next(queryset):
            if t[1] == self:
                return t

    @property
    def prev(self):
        """
        返回上一篇博文
        :return:
        """
        return self.prev_this_next[0]

    @property
    def next(self):
        """
        返回下一篇博文
        :return:
        """
        return self.prev_this_next[2]

    @staticmethod
    def has_read_permission(request):
        """
        表级权限控制(模型权限/全局权限),对指定操作开放读取权限
            list
            retrieve
        :param request:
        :return:
        """
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        """
        行级权限控制（对象权限），该权限需要在全局权限检测通过后检测
        指定当前博文对象的读取权限
        :param request:
        :return:
        """
        if request.user == self.author or self.post_type == enums.POST_TYPE_NOTIFICATION:
            return True
        if request.user.is_anonymous:
            return True if self.is_free and (self.status == enums.POST_STATUS_PUBLIC) else False

        checked = (self.status == enums.POST_STATUS_PUBLIC) and (
                    self.is_free or request.user.check_payment_status(self.post_sn))

        return True if checked else False

    @staticmethod
    def has_write_permission(request):
        """
        对指定操作开放写权限
            create
            update
            partial_update
            destroy
        :param request:
        :return:
        """
        return False if request.user.is_anonymous else True

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        """
        对当前对象开放指定的操作权限
        :param request:
        :return:
        """
        return self.author == request.user

    def on_cover_changed(self):
        if not self.cover_url:
            return
        cover_changed = (self.cover != 'blog/blog_cover/default.jpg') and not self.cover_url.endswith(str(self.cover))
        if cover_changed:
            cover_url = '%sblog/blog_cover/%s' % (settings.MEDIA_URL, self.cover) if not str(self.cover).startswith('blog/blog_cover') else '%s%s' % (settings.MEDIA_URL, self.cover)
            self.cover_url = cover_url

    def save(self, *args, **kwargs):
        self.on_cover_changed()
        return super(Post, self).save(*args, **kwargs)


class Resources(models.Model):
    post = models.ForeignKey(Post, verbose_name='所属博文', on_delete=models.CASCADE, blank=True, null=True,
                             related_name='resources')
    name = models.CharField(verbose_name='资源名称', max_length=50)
    resource = models.FileField(verbose_name='资源文件', max_length=200, upload_to='blog/resources/%Y/%m/')
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.datetime.now)

    class Meta:
        verbose_name = '博文资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
