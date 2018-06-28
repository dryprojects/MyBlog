from django.apps import AppConfig


class AgentConfig(AppConfig):
    name = 'agent'

    def ready(self):
        from agent import signals
