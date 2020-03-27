import environ

from .kms import env

ROOT_DIR = (
    environ.Path(__file__) - 3
)  # (chambers_app/config/settings/base.py - 3 = chambers_app/)
APPS_DIR = ROOT_DIR.path("chambers_app")

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    env.read_env(str(ROOT_DIR.path(".env")))
