from unittest import mock

import pytest
from django.test.client import encode_multipart
from requests.auth import HTTPBasicAuth
from rest_framework.test import RequestsClient, APIRequestFactory

from chambers_app.certificates.models import Certificate, CertificateDocument
from chambers_app.certificate_api_v0.views import DocumentUploadView
from chambers_app.organisations.factories import OrgFactory
from chambers_app.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db(transaction=True)


@mock.patch('chambers_app.certificates.tasks.IntergovClient.post_binary_document')
@mock.patch('chambers_app.certificates.tasks.IntergovClient.post_text_document')
@mock.patch('chambers_app.certificates.tasks.IntergovClient.post_message')
def test_integration_workflow(mock_post_message, mock_post_document, mock_post_binary):
    """
    Primitive but correct integration test, which creates certificate, uploads
    some dumb documents and marks it as "lodged".
    Doesn't check error-handling code branches (incorrect input, auth and so on),
    just displays that the workflow works fine in general.
    More specific unit tests are expected to test error handling and complicated cases
    (like document removed from the certificate and the certificate is not ready for
    lodging anymore).
    """
    mock_post_document.return_value = {"multihash": "QmNTWr4pXQcFd49PwgLBAPGjaedLkLXQU1c2EqfKV3K8RJ"}
    mock_post_binary.return_value = {"multihash": "QmNTWr4pXQcFd49PwgLBAPGjaedLkLXQU1c2EqfKV3K8RJ"}

    u1 = UserFactory()
    org = OrgFactory()

    c = RequestsClient()
    c.auth = HTTPBasicAuth(u1.username, 'password')

    message_body = {
        "org": str(org.pk),
        "dst_country": "CN",
        "exporter_info": "value",
        "producer_info": "value 02",
        "importer_info": "value 03",
        "goods_descr": "value of the goods description, which may be quite long or contain newlines",
    }

    mock_post_message.return_value = message_body.copy()

    # create some certificate
    resp = c.post(
        'http://testserver/api/certificate/v0/certificate/',
        data=message_body
    )
    assert resp.status_code == 201
    assert 'id' in resp.json()
    cert_id = resp.json().get('id')

    cert = Certificate.objects.get(
        org=org,
        pk=cert_id
    )

    assert cert.dst_country == 'CN'

    # upload some file
    cert.refresh_from_db()

    assert cert.status == cert.STATUS_DRAFT

    for file_type in (CertificateDocument.TYPE_INFORMATION_FORM, CertificateDocument.TYPE_EVIDENCE_OF_ORIGIN):
        factory = APIRequestFactory()
        data = {
            'type': file_type,
            'file': open('pytest.ini')
        }
        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        request = factory.post(
            f'http://testserver/api/certificate/v0/certificate/{cert_id}/document/',
            content, content_type=content_type
        )
        request.user = u1
        resp = DocumentUploadView.as_view()(request, pk=cert.pk)

        print(resp)
        assert resp.status_code == 201

    cert.refresh_from_db()
    assert cert.status == cert.STATUS_COMPLETE

    # mark as lodged

    resp = c.patch(
        f'http://testserver/api/certificate/v0/certificate/{cert_id}/status/',
        data={
            "status": "lodged"
        }
    )
    assert resp.status_code == 200

    cert.refresh_from_db()
    assert cert.status == cert.STATUS_SENT
