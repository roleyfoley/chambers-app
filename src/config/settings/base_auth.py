from .base_env import env

AUTH_USER_MODEL = "users.User"

# Django
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    'chambers_app.users.backends.MyOIDCAB',
]
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "account_login"
LOGOUT_REDIRECT_URL = "/"


# OIDC
OIDC_RP_CLIENT_ID = env('ICL_OIDC_RP_CLIENT_ID', default='')
OIDC_RP_CLIENT_SECRET = env('ICL_OIDC_RP_CLIENT_SECRET', default='')
# https://cognito-idp.ap-southeast-2.amazonaws.com/ap-southeast-2_SPmZvRR6R/.well-known/openid-configuration
OIDC_OP_AUTHORIZATION_ENDPOINT = env(
    'ICL_OIDC_OP_AUTHORIZATION_ENDPOINT',
    default="https://auth-icl-serv-mgmt-dir-auth-joco45x1e6.auth.ap-southeast-2.amazoncognito.com/oauth2/authorize"  # NOQA
)
OIDC_OP_TOKEN_ENDPOINT = env(
    'ICL_OIDC_OP_TOKEN_ENDPOINT',
    default="https://auth-icl-serv-mgmt-dir-auth-joco45x1e6.auth.ap-southeast-2.amazoncognito.com/oauth2/token"  # NOQA
)
OIDC_OP_USER_ENDPOINT = env(
    'ICL_OIDC_OP_USER_ENDPOINT',
    default="https://auth-icl-serv-mgmt-dir-auth-joco45x1e6.auth.ap-southeast-2.amazoncognito.com/oauth2/userInfo"  # NOQA
)
OIDC_RP_SIGN_ALGO = "RS256"
# it's faster but verbose
# OIDC_RP_IDP_SIGN_KEY = "<OP signing key in PEM or DER format>"
OIDC_OP_JWKS_ENDPOINT = env(
    'ICL_OIDC_OP_JWKS_ENDPOINT',
    default="https://cognito-idp.ap-southeast-2.amazonaws.com/ap-southeast-2_SPmZvRR6R/.well-known/jwks.json"
)
OIDC_STORE_ACCESS_TOKEN = True
OIDC_STORE_ID_TOKEN = True
# longer - more secure, 12 is fine for non-prod installations
OIDC_STATE_SIZE = 12
OIDC_NONCE_SIZE = 12


# Allauth
ACCOUNT_ALLOW_REGISTRATION = False
ACCOUNT_ALLOW_SOCIALREGISTRATION = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_ADAPTER = "chambers_app.users.adapters.AccountAdapter"
SOCIALACCOUNT_ADAPTER = "chambers_app.users.adapters.SocialAccountAdapter"
SOCIALACCOUNT_AUTO_SIGNUP = True

# https://django-allauth.readthedocs.io/en/latest/providers.html?highlight=github#github
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': [
            'user',
            'repo',
            'read:org',
        ],
    }
}
