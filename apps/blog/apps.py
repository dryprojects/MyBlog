from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'blog'
    verbose_name = '博文管理'

    def ready(self):
        from blog import signals