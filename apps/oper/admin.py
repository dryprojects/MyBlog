from django.contrib import admin
from django.utils.html import  format_html

from oper.models import Notification, NotificationUnReadCounter, BlogOwner, FriendshipLinks, Blacklist
# Register your models here.

@admin.register(Notification)
class NotificationModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    list_display = ['user', 'expert', 'has_read', 'published_time']
    list_display_links = ['expert']
    fieldsets = (
        ('用户消息', {
            'fields': ['content'],
            'classes': ('extrapretty',)
        }
         ),
        ('消息元数据', {
            'fields': [('user', 'has_read', 'published_time')],
            'classes': ('extrapretty',)
        }),
    )

    def expert(self, instance):
        return str(instance)

    expert.short_description = "摘要"


@admin.register(NotificationUnReadCounter)
class NotificationUnReadCounterModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'n_unread')
    readonly_fields = ['user', 'n_unread']


class BlogOwnerRecommendPostRelationShipInline(admin.TabularInline):
    model = BlogOwner.recommend_posts.rel.through
    extra = 1
    autocomplete_fields = ['post']
    verbose_name = '博主推荐博文'
    verbose_name_plural = verbose_name


@admin.register(BlogOwner)
class BlogOwnerModelAdmin(admin.ModelAdmin):
    inlines = [BlogOwnerRecommendPostRelationShipInline]
    fieldsets = [
        ('博主基本信息', {"fields": [('user', 'qq'), ('github', 'gitee')], 'classes': ('wide', 'extrapretty')}),
    ]
    exclude = ['recommend_posts']
    autocomplete_fields = ['user']


@admin.register(FriendshipLinks)
class FriendshipLinksModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'url']


@admin.register(Blacklist)
class BlacklistModelAdmin(admin.ModelAdmin):
    list_display = ['ip_addr', 'desc', 'add_time', 'expiration']
    fieldsets = (
        (
            "基本信息",
            {"fields": [('ip_addr', 'desc'), ('add_time', 'expiration')], 'classes': ('wide', 'extrapretty')}
        ),
    )