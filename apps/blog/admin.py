from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse

from blog.models import Post, Category, Tag, Resources
from kindeditor.widgets import KindTextareaWidget
from mdeditor.widgets import MdTextWidget

from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter

USE_ADMIN_SITE = True
ADD_PASSWORD_FORGET = False
if not USE_ADMIN_SITE:
    from django.contrib.auth.admin import User, UserAdmin, Group, GroupAdmin

    admin.site.unregister(User)
    admin.site.unregister(Group)
else:
    admin.site.site_header = "我的博客后台"
    admin.site.site_title = '我的博客'

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


class PostTagRelationShipInline(admin.TabularInline):
    model = Post.tags.rel.through
    extra = 1
    autocomplete_fields = ['tag']
    verbose_name = '博文标签'
    verbose_name_plural = verbose_name


class ResourcesInline(admin.TabularInline):
    model = Resources
    extra = 1


class PostModalAdmin(DraggableMPTTAdmin):
    """
    see detail:
        https://docs.djangoproject.com/en/2.0/intro/tutorial07/
    """
    fieldsets = [
        ('博文基本信息',
         {"fields": [('title', 'category', 'author'), ('url_object_id', 'origin_post_url', 'origin_post_from'), 'excerpt', 'content'], 'classes': ('wide', 'extrapretty')}),
        ('博文附加信息', {"fields": [('cover', 'cover_url', 'published_time', 'is_banner'), ('status', 'type', 'parent'),
                               ('n_praise', 'n_comments', 'n_comment_users', 'n_browsers')],
                    "classes": ('wide', 'extrapretty')}),
    ]
    inlines = [PostTagRelationShipInline, ResourcesInline]
    exclude = ['tags']
    readonly_fields = ['n_praise', 'n_comments', 'n_browsers', 'n_comment_users']
    list_display = ['tree_actions', 'get_posts', 'id', 'category', 'author', 'get_cover', 'type','published_time',
                    'status', 'is_banner', 'was_published_recently']
    list_editable = ['status', 'type', 'is_banner']
    list_filter = ('published_time',
                   ('parent', TreeRelatedFieldListFilter),
                   )
    list_per_page = 10
    list_display_links = ['get_posts']
    list_select_related = ('author', 'category')  # 缓存post相关外键对象，减少数据库查询
    autocomplete_fields = ['author', 'category', 'parent']  # django 2.0新增
    search_fields = ['title']
    date_hierarchy = 'published_time'

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
    actions = ['export_selected_post']

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

    def export_selected_post(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ct = ContentType.objects.get_for_model(queryset.model)
        redirect_url = reverse('blog:export-post')+"?ct=%s&ids=%s"%(ct.pk, ",".join(selected))
        return HttpResponseRedirect(redirect_url)

    export_selected_post.short_description = '导出选中博文'


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
