from django.apps import AppConfig


class TradeConfig(AppConfig):
    name = 'trade'
    verbose_name = '交易管理'

    def ready(self):
        from . import signals
