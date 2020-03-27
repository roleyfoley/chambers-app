import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class WebSubReceiverAppConfig(AppConfig):

    name = "chambers_app.websub_receiver"
    verbose_name = "WebSub Receiver module"

    def ready(self):
        from django.conf import settings

        if not settings.IS_LAMBDA_DEPLOYMENT:
            from chambers_app.websub_receiver.tasks import subscribe_to_notifications
            subscribe_to_notifications()
