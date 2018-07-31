from django.apps import AppConfig


class BloguserConfig(AppConfig):
    name = 'bloguser'
    verbose_name = '用户管理'

    def ready(self):
        from bloguser import signals
