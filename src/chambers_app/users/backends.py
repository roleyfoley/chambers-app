import logging

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

logger = logging.getLogger(__name__)


class MyOIDCAB(OIDCAuthenticationBackend):
    def get_username(self, claims):
        """Generate username based on claims."""
        return claims.get('email')
