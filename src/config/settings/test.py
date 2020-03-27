"""
With these settings, tests run faster.
"""

from .base import *  # noqa
from .base import env


DEBUG = False

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="VjqY3HCO5V3iNOZAGVxbyzSCJiI9y7RIfiOrjRbhYAeRXz1QDc4v0cYo1UrdqvZx",
)
TEST_RUNNER = "django.test.runner.DiscoverRunner"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG  # noqa F405
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025

CELERY_TASK_ALWAYS_EAGER = True
