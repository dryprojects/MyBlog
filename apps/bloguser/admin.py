from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext, gettext_lazy as _

from bloguser.models import UserProfile, MessageAuthCode
from bloguser.forms import BlogUserChangeForm, BlogUserAdminCreationForm


@admin.register(UserProfile)
class UserPrifileModelAdmin(UserAdmin):
    list_display = ('get_image', 'username', 'email', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'image', 'image_url', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['image_url']
    list_display_links = ['username', 'get_image']
    add_form = BlogUserAdminCreationForm

    def get_image(self, instance):
        return format_html("<img src='{}' alt='' width='50' height='50' />", instance.image_url)

    get_image.short_description = '用户头像'


@admin.register(MessageAuthCode)
class MessageAuthCodeModelAdmin(admin.ModelAdmin):
    list_display = ('phone_num', 'code', 'add_time', 'expiration', 'is_expired')
    fieldsets = (
        ("基本信息",
         {"fields": [('phone_num', 'code'), ('add_time', 'expiration')], 'classes': ('wide', 'extrapretty')}),
    )

    def is_expired(self, obj):
        return obj.is_expired

    is_expired.short_description = '是否过期'
    is_expired.boolean = True