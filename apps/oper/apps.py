from django.apps import AppConfig


class OperConfig(AppConfig):
    name = 'oper'
    verbose_name = '站点操作'

    def ready(self):
        from oper import signals
