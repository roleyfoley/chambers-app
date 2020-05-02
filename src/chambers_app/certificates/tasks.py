import json
import logging
import mimetypes

from django.conf import settings
from django.core.mail import send_mail

from intergov_client import IntergovClient

from chambers_app.certificates.models import Certificate, CertificateDocument
from chambers_app.taskapp.celery import app


logger = logging.getLogger(__name__)


@app.task
def notify_about_certificate_created(certificate_id):
    c = Certificate.objects.get(pk=certificate_id)
    send_mail(
        'Certificate application has been approved',
        """Just letting you know that your certificate {} has been lodged""".format(
            c
        ),
        settings.DEFAULT_FROM_EMAIL,
        [c.created_by.email],
        fail_silently=False,
    )


@app.task(ignore_result=True,
          max_retries=3, interval_start=10, interval_step=10, interval_max=50)
def send_certificate(certificate_id=None):
    """
    Create the certificate and send it to the upstream
    * upload all documents which must be uploaded to the upstream
    * create the message.object
      * link uploaded documents there
    * upload message object as well
    * send the message, linking to message object, which links to uploaded docs
    * save all details to the certificate object just for fun

    https://github.com/gs-immi/inter-customs-ledger/issues/322#issuecomment-503474417
    """
    ig_client = IntergovClient(country=settings.ICL_APP_COUNTRY)
    c = Certificate.objects.get(pk=certificate_id)
    assert c.status == Certificate.STATUS_LODGED
    # For each document we have - upload it to the intergov
    # this should be a celery chord with retries and so on, but not for MVP
    uploaded_documents_links = []
    for document in c.documents.filter(type__in=CertificateDocument.EXTERNAL_TYPES):
        # upload the document
        d_info = ig_client.post_binary_document(c.dst_country, document.file)
        mt, enc = mimetypes.guess_type(document.filename, strict=False)
        # save result to links
        uploaded_documents_links.append(
            {
                'TYPE1': 'document',
                'TYPE2': document.type,
                'name': document.filename,
                'ct': mt or 'binary/octet-stream',
                'link': d_info['multihash']
            }
        )

    # Upload the certificate JSON body as a machine-readable document
    certificate_body = json.dumps({
        "TYPE": "CertificateOfOrigin",
        "FORMAT": "EDI3.draft.2019-05-12.01",  # TODO: UN.blabla.edi3.2019-06.1

        'id': str(c.id),
        'dst_country': str(c.dst_country),
        'org.name': settings.CHAMBERS_ORG_NAME,
        'org.id': settings.CHAMBERS_ORG_ID,
        'body': {
            'exporter_info': c.exporter_info,
            'producer_info': c.producer_info,
            'importer_info': c.importer_info,
            'transport_info': c.transport_info,
            'remarks': c.remarks,
            'item_no': c.item_no,
            'packages_marks': c.packages_marks,
            'goods_descr': c.goods_descr,
            'hs_code': c.hs_code,
            'invoice_info': c.invoice_info,
            'origin_criterion': c.origin_criterion,
        }
    })
    cert_body_info = ig_client.post_text_document(c.dst_country, certificate_body)
    uploaded_documents_links.append(
        {
            'TYPE1': 'certificate',
            'TYPE2': 'EDI3.draft.2019-05-12.01',
            'ct': 'application/json',
            'link': cert_body_info['multihash']
        }
    )

    logger.info(
        "The following documents were uploaded for %s: %s",
        c, uploaded_documents_links
    )

    c.intergov_details['links'] = uploaded_documents_links

    # upload the object itself. which is just some JSON linking to things
    object_body = json.dumps({
        # not much to include here by the way. it's just links field is interesting
        'type': 'certificate-of-origin',
        'format': '0.0.1',
        'links': uploaded_documents_links,
    })
    object_info = ig_client.post_text_document(c.dst_country, object_body)
    logger.info("Uploaded certificate object %s as %s", object_body, object_info)

    c.intergov_details['object_hash'] = object_info['multihash']

    # Post the message
    message_json = {
        "predicate": "UN.CEFACT.Trade.CertificateOfOrigin.created",
        "sender": settings.ICL_CHAMBERS_APP_COUNTRY,
        "receiver": str(c.dst_country),
        "subject": "{}.{}.{}".format(
            settings.ICL_CHAMBERS_APP_COUNTRY.upper(),
            settings.CHAMBERS_ORG_ID.replace('.', '-'),
            c.id
        ),
        "obj": object_info['multihash'],
    }

    posted_message = ig_client.post_message(message_json)
    if not posted_message:
        raise Exception("Unable to post message, trying again")
    else:
        c.status = Certificate.STATUS_SENT
    c.intergov_details['sent_message'] = posted_message
    c.save()
    logging.info("Posted message %s", posted_message)
    return
