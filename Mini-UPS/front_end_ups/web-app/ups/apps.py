from django.apps import AppConfig


class UpsConfig(AppConfig):
    name = 'ups'

    def ready(self):
        import ups.signals
