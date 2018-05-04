from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext, gettext_lazy as _

from bloguser.models import UserProfile


@admin.register(UserProfile)
class UserPrifileModelAdmin(UserAdmin):
    list_display = ('get_image', 'username', 'email', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'image', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (('username', 'image'), 'password1', 'password2'),
        }),
    )

    def get_image(self, instance):
        return format_html("<img src='{}' alt='' width='50' height='50' />", instance.image.url)
    get_image.short_description = '用户头像'