from django.apps import AppConfig


class OperConfig(AppConfig):
    name = 'oper'

    def ready(self):
        from oper import signals
