from django.apps import AppConfig


class EventhubConfig(AppConfig):
    name = 'eventhub'

    def ready(self):
        import eventhub.signals  # noqa: F401
