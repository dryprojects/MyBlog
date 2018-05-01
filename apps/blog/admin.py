from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.contenttypes.admin import GenericStackedInline, GenericTabularInline
from django.utils.html import format_html
from django.db import models
from django.urls import reverse

from blog.models import Post, Category, Tag, Resources
from comment.models import Comment
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


# class CommentInline(GenericTabularInline):
#     model = Comment
#     extra = 1
#     autocomplete_fields = ['author']



class PostTagRelationShipInline(admin.TabularInline):
    model = Post.tags.rel.through
    extra = 1
    autocomplete_fields = ['tag']


class ResourcesInline(admin.TabularInline):
    model = Resources
    extra = 1


class PostModalAdmin(admin.ModelAdmin):
    """
    see detail:
        https://docs.djangoproject.com/en/2.0/intro/tutorial07/
    """
    fieldsets = [
        ('博文基本信息',  {"fields":[('title', 'category', 'author'), ('excerpt', 'status'), 'content'], 'classes': ('wide', 'extrapretty')}),
        ('博文附加信息',  {"fields":[('cover', 'published_time'), ('n_praise', 'n_comments', 'n_browsers')], "classes":('wide', 'extrapretty')}),
    ]
    inlines = [PostTagRelationShipInline, ResourcesInline]
    exclude = ['tags']
    readonly_fields = ['n_praise', 'n_comments', 'n_browsers']
    list_display = ['id', 'title', 'category', 'author', 'get_cover', 'published_time', 'status','was_published_recently']
    list_editable = ['status']
    list_filter = ['published_time']
    list_per_page = 10
    list_display_links = ['title']
    list_select_related = ('author', 'category') #缓存post相关外键对象，减少数据库查询
    autocomplete_fields = ['author', 'category'] #django 2.0新增
    search_fields = ['title']
    date_hierarchy = 'published_time'

    # formfield_overrides = {
    #     models.TextField:{
    #         'widget':KindTextareaWidget(config={
    #             'width':"800px",
    #             'height':"300px",
    #             "filterMode":False,
    #             "uploadJson":'/kindeditor/upload/'
    #         })
    #     }
    # }
    formfield_overrides = {
        models.TextField:{
            'widget': MdTextWidget
        }
    }

    def get_cover(self, object):
        return format_html("<a href='{}'><img src='{}' alt='' width='150'/></a>", object.get_absolute_url(), object.cover.url)
    get_cover.short_description = '封面'



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