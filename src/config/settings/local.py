from .base import *  # noqa
from .base import env

DEBUG = True
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="q1dC1Zmvb6Vr50ivv26gjkiEOVz4dLUIXqwFJRSgMg5tsJFAbzuMCguF3aI5L8V5",
)
ALLOWED_HOSTS = ["*"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG  # noqa F405

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025

INSTALLED_APPS += ["debug_toolbar"]  # noqa F405
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if env("USE_DOCKER", default="no") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]

INSTALLED_APPS += ["django_extensions"]  # noqa F405

CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_ALWAYS_EAGER = env.bool(
    "ICL_CELERY_TASK_ALWAYS_EAGER",
    default=True,
)
