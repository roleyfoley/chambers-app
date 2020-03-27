import logging

from django.conf import settings
from intergov_client import IntergovClient

from chambers_app.taskapp.celery import app
from chambers_app.utils.monitoring import statsd_timer

logger = logging.getLogger(__name__)


@statsd_timer("task.subscribe_to_notifications.execute")
def _subscribe_to_notifications():
    from .views import MsgNotificationReceiveView

    try:
        ic = IntergovClient(country=settings.ICL_APP_COUNTRY)
        # subscribe on message-related notifications
        # to receive foreign messages
        for pred in MsgNotificationReceiveView.ACCEPTED_PREDICATES:
            logger.info("Subscribing the %s...", pred)
            ic.subscribe(
                predicate=pred,
                callback=settings.ICL_CHAMBERS_APP_HOST + "/websub/channel/messages/news/",
            )
        # subscribe on cert status change notifications
        # to control the status of sent certificates
        ic.subscribe(
            predicate='message.status.change',
            callback=(
                settings.ICL_CHAMBERS_APP_HOST +
                "/websub/channel/cert-status-update/news/"
            ),
        )
    except Exception as e:
        logger.exception(e)


@app.task(ignore_result=True, max_retries=3)
def subscribe_to_notifications():
    _subscribe_to_notifications()
