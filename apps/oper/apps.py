from django.apps import AppConfig


class OperConfig(AppConfig):
    name = 'oper'
    verbose_name = '用户操作管理'

    def ready(self):
        from oper import signals
