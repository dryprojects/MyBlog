import collections

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse

from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter
from import_export import resources
from import_export.admin import ImportExportMixin, ImportExportActionModelAdmin
from import_export.fields import Field, NOT_PROVIDED
from guardian.admin import GuardedModelAdminMixin

from blog.models import Post, Category, Tag, Resources
from blog import enums
from kindeditor.widgets import KindTextareaWidget
from mdeditor.widgets import MdTextWidget
from bloguser.models import UserProfile

USE_ADMIN_SITE = True
ADD_PASSWORD_FORGET = False
if not USE_ADMIN_SITE:
    from django.contrib.auth.admin import User, UserAdmin, Group, GroupAdmin

    admin.site.unregister(User)
    admin.site.unregister(Group)
else:
    admin.site.site_header = enums.ADMIN_SITE_HEADER_TITLE
    admin.site.site_title = enums.ADMIN_SITE_TITLE

# Register your models here.
if not USE_ADMIN_SITE:
    class BlogAdminSite(AdminSite):
        """
        自定义一个博客管理后台
            如果用到contrib,auth,User需要把它先从原来的站点反注册，然后注册到自定义的站点
            模板使用的是admin自带的，可以自己覆盖,或者指定模板路径
        """
        site_header = "我的自定义博客后台"
        site_title = "我的博客"


class MyField(Field):
    """
    自定义博文资源字段类型
    方便做数据转换，清理
    """

    def clean(self, data):
        try:
            value = data[self.column_name]
        except KeyError:
            raise KeyError("Column '%s' not found in dataset. Available "
                           "columns are: %s" % (self.column_name, list(data)))
        value = self.get_column_field_mapping(self.column_name, value)
        try:
            value = self.widget.clean(value, row=data)
        except ValueError as e:
            raise ValueError("Column '%s': %s" % (self.column_name, e))

        if value in self.empty_values and self.default != NOT_PROVIDED:
            if callable(self.default):
                return self.default()
            return self.default

        return value

    def get_column_field_mapping(self, column_name, value=None):
        """
        导入数据时，对应字段转换为数据库字段
        :return:
        """
        m_c = {
            '博文标签': self.get_tags_m2m_ids,
            '是否轮播': {
                '是': True,
                '否': False,
            },
            '是否免费': {
                '是': True,
                '否': False,
            },
            '编辑状态': {
                '公开': enums.POST_STATUS_PUBLIC,
                '私有': enums.POST_STATUS_PRIVATE,
            },
            '博文类型': {
                '博文': enums.POST_TYPE_POST,
                '公告': enums.POST_TYPE_NOTIFICATION,
            }
        }
        m_v = m_c.get(column_name, None)
        if m_v is None:
            return value  # 使用默认

        if callable(m_v):
            return m_v(value)

        return m_v[value]

    def get_tags_m2m_ids(self, value):
        # 博文标签
        tag_names = value
        tag_list = []
        if tag_names != "":
            tag_name_list = tag_names.split(',')
            for tag_name in tag_name_list:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tag_list.append(str(tag.id))
        return ",".join(tag_list)


class PostResource(resources.ModelResource):
    """
    博文导入导出资源定义
    see https://django-import-export.readthedocs.io/en/latest/getting_started.html#customize-resource-options
    """
    DEFAULT_RESOURCE_FIELD = MyField

    class Meta:
        model = Post
        fields_column_mapping = {
            'parent__title': '上篇博文标题',
            'title': '博文标题',
            'cover_url': '博文封面url',
            'category__name': '博文分类名',
            'tags': '博文标签',
            'author__username': '作者',
            'author__email': '作者邮箱',
            'content': '内容',
            'status': '编辑状态',
            'n_praise': '点赞数',
            'n_browsers': '浏览数',
            'published_time': '发表时间',
            'post_type': '博文类型',
            'is_banner': '是否轮播',
            'is_free': '是否免费',
            'origin_post_url': '原博文地址',
            'origin_post_from': '原博文出处',
            'url_object_id': '博文唯一标识'
        }
        fields = fields_column_mapping.keys()
        import_id_fields = ('url_object_id',)
        export_order = fields
        skip_unchanged = True
        report_skipped = False

    @classmethod
    def field_from_django_field(cls, field_name, django_field, readonly):
        """
        Returns a Resource Field instance for the given Django model field.
        """

        FieldWidget = cls.widget_from_django_field(django_field)
        widget_kwargs = cls.widget_kwargs_for_field(field_name)
        field = cls.DEFAULT_RESOURCE_FIELD(
            attribute=field_name,
            column_name=cls._meta.fields_column_mapping[field_name],
            widget=FieldWidget(**widget_kwargs),
            readonly=readonly,
            default=django_field.default,
        )
        return field

    def get_column_fields_mapping(self, row, **kwargs):
        """
        将column名称转换为模型字段名
        :param row:
        :param kwargs:
        :return:
        """
        od_row = collections.OrderedDict()
        cf_mapping = dict(zip(self._meta.fields_column_mapping.values(), self._meta.fields_column_mapping.keys()))
        for key in row.keys():
            od_row[cf_mapping[key]] = row[key]

        return od_row

    def dehydrate_tags(self, post):
        """
        左边（数据库）和右边（文件）作比较时都会调用
        :param post:
        :return:
        """
        try:
            ts = post.tags.all()
            r = [tag.name for tag in ts]
            # 这里抓异常是因为，当需要新建一个博文实例时候，调用到这里还不会被保存。这时m2m是不可用的
        except Exception as e:
            # 这里新建的对象不给标签也可以，文件里有的话，会最终补丁到数据库
            return ''
        return ",".join(r)

    def dehydrate_is_banner(self, post):
        if post.is_banner is True:
            return "是"
        elif post.is_banner is False:
            return "否"
        else:  # 当计算文件（右边）内容时会调用
            return post.is_banner

    def dehydrate_is_free(self, post):
        if post.is_free is True:
            return "是"
        elif post.is_free is False:
            return "否"
        else:  # 当计算文件（右边）内容时会调用
            return post.is_free

    def dehydrate_status(self, post):
        if post.status == enums.POST_STATUS_PUBLIC:
            return '公开'
        elif post.status == enums.POST_STATUS_PRIVATE:
            return '私有'
        else:
            return post.status

    def dehydrate_post_type(self, post):
        if post.post_type == enums.POST_TYPE_POST:
            return '博文'
        elif post.post_type == enums.POST_TYPE_NOTIFICATION:
            return '公告'
        else:
            return post.post_type

    def init_instance(self, row=None):
        """
        如果数据库当中不存在文件里对应的行，
        则需要新建一个对象，与文件里的作比较
        :param row:
        :return:
        """
        # 找出父级博文, 如果找不到推迟到父级博文创建后关联
        row = self.get_column_fields_mapping(row)

        try:
            ptitle = row.get('parent__title', None)
            if ptitle:
                parent = Post.objects.get(title=ptitle)
            else:
                parent = None
        except Post.DoesNotExist:
            parent = None
        # 创建或者找出对应分类
        category, created = Category.objects.get_or_create(name=row.get('category__name'))
        # 创建或者找出对应的作者
        author, created = UserProfile.objects.get_or_create(email=row.get('author__email'),
                                                            defaults={'username': row.get('author__username')})
        post = Post(
            parent=parent,
            category=category,
            author=author,
        )
        return post


class PostTagRelationShipInline(admin.TabularInline):
    model = Post.tags.rel.through
    extra = 1
    autocomplete_fields = ['tag']
    verbose_name = '博文标签'
    verbose_name_plural = verbose_name


class ResourcesInline(admin.TabularInline):
    model = Resources
    extra = 1


class PostModalAdmin(GuardedModelAdminMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    """
    see detail:
        https://docs.djangoproject.com/en/2.0/intro/tutorial07/
    """
    resource_class = PostResource

    fieldsets = [
        ('博文基本信息',
         {"fields": [('title', 'category', 'author'), ('url_object_id', 'origin_post_url', 'origin_post_from'),
                     'excerpt', 'content'], 'classes': ('wide', 'extrapretty')}),
        ('博文附加信息', {"fields": [('cover', 'cover_url', 'published_time', 'is_banner'),
                               ('status', 'post_type', 'parent', 'is_free'),
                               ('n_praise', 'n_comments', 'n_comment_users', 'n_browsers')],
                    "classes": ('wide', 'extrapretty')}),
    ]
    inlines = [PostTagRelationShipInline, ResourcesInline]
    exclude = ['tags']
    readonly_fields = ['n_praise', 'n_comments', 'n_browsers', 'n_comment_users']
    list_display = ['tree_actions', 'get_posts', 'id', 'category', 'author', 'get_cover', 'post_type', 'published_time',
                    'status', 'is_banner', 'is_free', 'was_published_recently']
    list_editable = ['status', 'post_type', 'is_banner', 'is_free']
    list_filter = ('published_time',
                   ('parent', TreeRelatedFieldListFilter),
                   )
    list_per_page = 10
    list_display_links = ['get_posts']
    list_select_related = ('author', 'category')  # 缓存post相关外键对象，减少数据库查询
    autocomplete_fields = ['author', 'category', 'parent']  # django 2.0新增
    search_fields = ['title']
    date_hierarchy = 'published_time'
    ordering = ('-published_time',)

    # formfield_overrides = {
    #     models.TextField:{
    #         'widget':KindTextareaWidget
    #     }
    # }
    formfield_overrides = {
        models.TextField: {
            'widget': MdTextWidget
        }
    }

    # actions = ['export_selected_post']

    def get_cover(self, object):
        return format_html("<a href='{}'><img src='{}' alt='' width='150' height='100'/></a>",
                           object.get_absolute_url(), object.cover_url)

    get_cover.short_description = '封面'

    def get_posts(self, instance):
        return format_html(
            '<div style="text-indent:{}px">{}</div>',
            instance._mpttfield('level') * self.mptt_level_indent,
            instance.title,  # Or whatever you want to put here
        )

    get_posts.short_description = '博文'

    # def export_selected_post(self, request, queryset):
    #     selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    #     ct = ContentType.objects.get_for_model(queryset.model)
    #     redirect_url = reverse('blog:export-post')+"?ct=%s&ids=%s"%(ct.pk, ",".join(selected))
    #     return HttpResponseRedirect(redirect_url)
    #
    # export_selected_post.short_description = '导出选中博文'


class CategoryModelAdmin(DraggableMPTTAdmin):
    list_display = ['tree_actions', 'get_categories']
    fields = ['name', 'parent']
    search_fields = ['name']
    autocomplete_fields = ['parent']
    list_display_links = ['get_categories']
    list_filter = (
        ('parent', TreeRelatedFieldListFilter),
    )

    def get_categories(self, instance):
        return format_html(
            '<div style="text-indent:{}px">{}</div>',
            instance._mpttfield('level') * self.mptt_level_indent,
            instance.name,  # Or whatever you want to put here
        )

    get_categories.short_description = '分类'


class TagModelAdmin(admin.ModelAdmin):
    fields = ['name']
    search_fields = ['name']


if not USE_ADMIN_SITE:
    admin_site = BlogAdminSite(name='admin')
    for model, model_admin in [(Post, PostModalAdmin), (Category, CategoryModelAdmin), \
                               (Tag, TagModelAdmin), (User, UserAdmin), (Group, GroupAdmin)]:
        admin_site.register(model, model_admin)
else:
    for model, model_admin in [(Post, PostModalAdmin), (Category, CategoryModelAdmin), \
                               (Tag, TagModelAdmin)]:
        admin.site.register(model, model_admin)
