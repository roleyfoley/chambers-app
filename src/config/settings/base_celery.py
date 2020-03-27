import datetime

from .base_env import env


CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERYD_TASK_TIME_LIMIT = 5 * 60
CELERYD_TASK_SOFT_TIME_LIMIT = 60
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_WORKER_LOG_COLOR = False
CELERY_WORKER_REDIRECT_STDOUTS_LEVEL = 'INFO'
# we don't have any tasks which result is checked (yet)
CELERY_TASK_IGNORE_RESULT = True

CELERY_BROKER_TRANSPORT_OPTIONS = {
    'max_retries': 4,
    'interval_start': 0,
    'interval_step': 0.5,
    'interval_max': 3,
}

CELERY_BEAT_SCHEDULE = {
    'subscribe_to_notifications': {
        'task': 'chambers_app.websub_receiver.tasks.subscribe_to_notifications',
        'schedule': datetime.timedelta(minutes=30),
    },
}
