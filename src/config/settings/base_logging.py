from .base_env import env

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s [%(asctime)s] %(name)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# JSON formatter for sending logs to ES
LOG_FORMATTER_JSON = env.bool('ICL_LOG_FORMATTER_JSON', default=False)
if LOG_FORMATTER_JSON:
    LOGGING['formatters']['json'] = {
        '()': 'config.settings.json_log_formatter.JsonFormatter',
    }
    LOGGING['handlers']['console']['formatter'] = 'json'
