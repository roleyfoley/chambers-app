import logging
from .base_env import env

ICL_CHAMBERS_APP_COUNTRY = env('ICL_CHAMBERS_APP_COUNTRY', default='AU')
ICL_APP_COUNTRY = ICL_CHAMBERS_APP_COUNTRY

# for the WebSub notifications
ICL_CHAMBERS_APP_HOST = env(
    'ICL_CHAMBERS_APP_HOST',
    default='http://chambers-app-django.intergov-apis-external:8010'
)
# and the relative url is /websub/channel/{something}/

CSS_COUNTRY = env(
    'ICL_CSS_COUNTRY',
    default='SG'
).lower()
if CSS_COUNTRY not in ('au', 'sg', 'cn'):
    logging.warning("Country %s is unsupported", CSS_COUNTRY)
