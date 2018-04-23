from django.contrib import admin
from oper.models import Notification, NotificationUnReadCounter
# Register your models here.

@admin.register(Notification)
class NotificationModelAdmin(admin.ModelAdmin):
    pass


@admin.register(NotificationUnReadCounter)
class NotificationUnReadCounter(admin.ModelAdmin):
    pass

