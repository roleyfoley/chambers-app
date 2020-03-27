import json
import logging
import urllib
from http import HTTPStatus

import requests

from django.conf import settings

logger = logging.getLogger(__name__)


class IntergovClient(object):
    """
    Helper class to make the intergov API calls
    """

    def _get_documents_api_auth(self):
        return {
            'Authorization': 'JWTBODY {}'.format(
                json.dumps({
                    "sub": "documents-api",
                    "party": "app",
                    "country": self.COUNTRY,
                })
            )
        }

    def __init__(self, country):
        assert len(country) == 2 and country.upper() == country
        self.COUNTRY = country
        self.POST_MESSAGE_API_ENDPOINT = urllib.parse.urlunparse(
            (
                settings.IGL_APIS['message']['schema'],
                settings.IGL_APIS['message']['netloc'],
                settings.IGL_APIS['message']['pathes']['post']['message'],
                None, None, None,
            )
        )
        self.POST_DOCUMENT_API_ENDPOINT = urllib.parse.urlunparse(
            (
                settings.IGL_APIS['document']['schema'],
                settings.IGL_APIS['document']['netloc'],
                settings.IGL_APIS['document']['pathes']['post']['document'],
                None, None, None,
            )
        )

        self.RETRIEVE_DOCUMENT_ENDPOINT = urllib.parse.urlunparse(
            (
                settings.IGL_APIS['document']['schema'],
                settings.IGL_APIS['document']['netloc'],
                settings.IGL_APIS['document']['pathes']['get'],
                None, None, None,
            )
        )

        self.SUBSCRIBE_ENDPOINT = settings.IGL_APIS['subscription']

    def post_message(self, message_json):
        """
        Posts a message to message TX API, returns posted message body
        (with sender_ref supposedly to be attached).
        Raises exceptions if any.
        """

        resp = requests.post(self.POST_MESSAGE_API_ENDPOINT, json=message_json)

        if resp.status_code != HTTPStatus.CREATED:
            logger.error(
                "Unable to publish message: %s %s",
                resp.status_code,
                resp.text[:2000]
            )
            raise Exception(
                "url:{}\n"
                "resp:{}".format(
                    self.POST_MESSAGE_API_ENDPOINT,
                    resp.text
                )
            )
        return resp.json()

    def post_text_document(self, receiver, document_body):
        """
        Accepts str with the document content,
        returns JSON with some document info (at least `multihash` str field)
        """
        files = {
            'document': ('document.json', document_body)
        }
        resp = requests.post(
            self.POST_DOCUMENT_API_ENDPOINT.format(
                country_name=receiver
            ),
            files=files,
            headers=self._get_documents_api_auth(),
        )
        if resp.status_code != HTTPStatus.OK:
            # unexpected but we still need to react somehow
            raise Exception("Unable to post document: %s" % resp.text[:2000])
        return resp.json()

    def post_binary_document(self, receiver, document_stream):
        files = {
            'document': ('document.json', document_stream)
        }
        resp = requests.post(
            self.POST_DOCUMENT_API_ENDPOINT.format(
                country_name=receiver
            ),
            files=files,
            headers=self._get_documents_api_auth(),
        )
        if resp.status_code != HTTPStatus.OK:
            # unexpected but we still need to react somehow
            raise Exception("Unable to post document: %s" % resp.text[:2000])
        return resp.json()

    def retrieve_text_document(self, *args, **kwargs):
        return self.retrieve_document(*args, **kwargs)

    def retrieve_document(self, document_multihash):
        endpoint = f"{self.RETRIEVE_DOCUMENT_ENDPOINT}{document_multihash}"
        resp = requests.get(
            endpoint,
            headers=self._get_documents_api_auth(),
        )
        if resp.status_code == 200:
            return resp.content
        else:
            raise Exception(f"Unable to retrieve document: {resp.status_code}")

    def subscribe(self, predicate, callback):
        resp = requests.post(
            self.SUBSCRIBE_ENDPOINT,
            data={
                'hub.callback': callback,
                'hub.topic': predicate,
                'hub.mode': 'subscribe'
            }
        )
        if resp.status_code != 202:
            raise Exception(
                "Unable to subscribe to {}: {}, {}".format(
                    predicate,
                    resp, resp.text[:2000],
                )
            )
