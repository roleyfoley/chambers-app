import os
import base64
import json
import logging

import boto3

from environ import Env as PureEnv

logger = logging.getLogger(__name__)
BASE64_PREFIX_1 = 'base64:'
BASE64_PREFIX_2 = 'kms+base64:'
AWS_REGION = os.environ.get('AWS_REGION', None)


def decrypt_kms_data(encrypted_data):
    """Decrypt KMS encoded data."""
    if not AWS_REGION:
        logger.error(
            "Trying to decrypt KMS value but no AWS region set"
        )
        return None

    kms = boto3.client('kms', region_name=AWS_REGION)
    decrypted = kms.decrypt(CiphertextBlob=encrypted_data)

    if decrypted.get('KeyId'):
        # Decryption succeed
        decrypted_value = decrypted.get('Plaintext', '')
        if isinstance(decrypted_value, bytes):
            decrypted_value = decrypted_value.decode('utf-8')
        return decrypted_value


def decrypt_kms_file(encrypted_filename):
    """
    Return the content of decrypted KMS file. Requires file to have .kms extension.
    Raises a warning and returns the input file content if decryption fails.
    """
    with open(encrypted_filename, 'rb') as cypherfile:
        cyphertext = cypherfile.read()

    if not AWS_REGION:
        logger.error(
            "Trying to decrypt KMS value but no AWS region set"
        )
        return cyphertext

    kms = boto3.client('kms', region_name=AWS_REGION)
    decrypted = kms.decrypt(
        CiphertextBlob=base64.b64decode(
            cyphertext
        )
    )

    if decrypted.get('KeyId'):
        # Decryption succeed
        decrypted_value = decrypted.get('Plaintext', '')
        return decrypted_value
    logger.warning("Failed to decrypt the KMS file %s", encrypted_filename)
    return cyphertext


def string_or_b64kms(value):
    """Check if value is base64 encoded - if yes, decode it using KMS."""
    if not value:
        return value

    try:
        # Check if environment value base64 encoded
        if isinstance(value, (str, bytes)):
            encrypted_value = None
            if value.startswith(BASE64_PREFIX_1):
                encrypted_value = value[len(BASE64_PREFIX_1):]
            elif value.startswith(BASE64_PREFIX_2):
                encrypted_value = value[len(BASE64_PREFIX_2):]
            else:
                # non-encrypted value
                return value
            # If yes, decode it using AWS KMS
            data = base64.b64decode(encrypted_value)
            decrypted_value = decrypt_kms_data(data)

            # If decryption succeed, use it
            if decrypted_value:
                value = decrypted_value
    except Exception as e:
        logger.exception(e)
    return value


class Env(PureEnv):
    """Extends environ.Env with added AWS KMS encryption support."""

    def __call__(self, *args, **kwargs):
        value = super().__call__(*args, **kwargs)
        return string_or_b64kms(value)

    def json(self, *args, **kwargs):
        raw_value = string_or_b64kms(
            self(*args, **kwargs)
        )
        if isinstance(raw_value, (bytes, str, bytearray)):
            return json.loads(raw_value)
        else:
            return raw_value

    def db_url(self, var=PureEnv.DEFAULT_DATABASE_ENV, default=PureEnv.NOTSET, engine=None):
        """Returns a config dictionary, defaulting to DATABASE_URL.
        :rtype: dict
        """
        value = string_or_b64kms(self.get_value(var, default=default))
        return self.db_url_config(value, engine=engine)

    db = db_url

env = Env()  # NOQA
