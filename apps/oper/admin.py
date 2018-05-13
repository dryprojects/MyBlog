from django.contrib import admin
from oper.models import Notification, NotificationUnReadCounter
# Register your models here.

@admin.register(Notification)
class NotificationModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    list_display = ['user', 'expert', 'has_read', 'published_time']
    list_display_links = ['expert']
    fieldsets = (
        ('用户消息',{
            'fields':['content'],
            'classes':('extrapretty',)
            }
        ),
        ('消息元数据',{
           'fields':[('user', 'has_read', 'published_time')],
            'classes': ('extrapretty',)
        }),
    )

    def expert(self, instance):
        return str(instance)
    expert.short_description = "摘要"


@admin.register(NotificationUnReadCounter)
class NotificationUnReadCounter(admin.ModelAdmin):
    list_display = ('user', 'n_unread')
    readonly_fields = ['user', 'n_unread']

