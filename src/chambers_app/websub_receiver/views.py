import json
import logging

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils import timezone
from django.utils.decorators import method_decorator
from intergov_client.predicates import Predicates

from chambers_app.certificates.models import Certificate
from chambers_app.utils.monitoring import statsd_timer

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class BaseNotificationReceiveView(View):
    """
    Base view which just reads the body and passes it to the
    _process_notification procedure, which is defined for subclasses.

    curl -XPOST http://0.0.0.0:8010/websub/channel/lalala/ \
    -H "Content-Type: application/json" \
    -H "Accept: application/json; indent=2" \
    -d '{
        "sender": "CN",
        "receiver": "AU",
        "subject": "some certificate subject",
        "obj": "QmQtYtUS7K1AdKjbuMsmPmPGDLaKL38M5HYwqxW9RKW49n",
        "predicate": "UN.CEFACT.Trade.Certificate.created",
        "sender_ref": "1e6cc328-c3a6-4353-a8ee-bca60afebc48"
      }
    '
    """

    def _process_notification(self, *args, **kwargs):
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):
        # websub spec says that we process the object async, but
        # for MVP it's fine to do it sync, but quickly
        try:
            notification_body = json.loads(request.body)
        except json.decoder.JSONDecodeError as e:
            return HttpResponseBadRequest(f"Incorrect JSON provided ({str(e)}\n")
        logger.info(
            "Received notification: channel %s, body %s",
            request.path_info,
            notification_body,
        )
        try:
            result = self._process_notification(notification_body)
        except Exception as e:
            logger.exception(e)
            result = None
        return result or HttpResponse()


class MsgNotificationReceiveView(BaseNotificationReceiveView):

    ACCEPTED_PREDICATES = [
        Predicates.CO_ACQUITTED.upper()
    ]

    @csrf_exempt
    @statsd_timer("view.MsgNotificationReceiveView.dispatch")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def _process_notification(self, notification_body):
        incoming_message = notification_body
        predicate = incoming_message['predicate']
        if predicate.upper() not in self.ACCEPTED_PREDICATES:
            logger.error(
                "Ignoring predicate %s, should't be subscribed at it at all",
                predicate
            )
            return HttpResponse("Ignored, not interesting predicate")
        else:
            logger.info(
                'Predicate %s is accepted and will be processed', predicate
            )
        if predicate.upper() == Predicates.CO_ACQUITTED.upper():
            self._handle_co_acquittal(incoming_message)

    def _handle_co_acquittal(self, message):
        """
        Process certificate acquittal
        Ideally it should be moved to some background task as well
        """
        # TODO: validate the previous status is `accepted` or `sent`
        country, org_id, cert_id = message['subject'].split('.')
        cert = Certificate.objects.get(
            id=cert_id,
            org_id=org_id,
        )
        cert.acquitted_at = timezone.now()
        if message not in cert.acquitted_details:
            cert.acquitted_details.append(message)
        cert.status = Certificate.STATUS_ACQUITTED
        cert.save()


class CertStatusNotificationView(BaseNotificationReceiveView):
    """
    Certificate (sent) has changed it's status (to accepted or rejected)

    Expects to receive a dict with next fields:
    {
        'subject': 'AU.{org-id}.{cert-id}',
        'status': 'new-status'
    }
    """

    @csrf_exempt
    @statsd_timer("view.CertStatusNotificationView.dispatch")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def _process_notification(self, event):
        # TODO: validate the previous status is `sent` or equal to the new one
        country, org_id, cert_id = event['subject'].split('.')
        cert = Certificate.objects.get(
            id=cert_id,
            org_id=org_id,
        )

        if event['predicate'].upper() == "message.status.change".upper():
            # warning: status transitions are more complicate, but it's enough for start
            fit_statuses = (
                Certificate.STATUS_LODGED,
                Certificate.STATUS_SENT,
                Certificate.STATUS_REJECTED,
            )
            if cert.status in fit_statuses:
                logger.info(
                    "Changing status from %s to %s for %s",
                    cert.status, event['status'], cert
                )
                cert.status = event['status']
                cert.save()
        return
