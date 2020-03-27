# don't forget to add django app container to intergov apis docker network
# docker connect <network_name> <container_name>
# I borrowed naming from urllib

from .base_env import env

IGL_APIS = {
    'document': {
        'schema': env("IGL_DOCAPI_SCHEMA", default='http'),
        'netloc': '{}:{}'.format(
                            env('IGL_DOCAPI_HOST', default='intergov_document_api'),
                            env('IGL_DOCAPI_PORT', default='5103')),
        'pathes': {
            'post': {
                'document': '/countries/{country_name}'
            },
            'get': '/'
        }
    },
    'message': {
        'schema': env("IGL_MESSAGEAPI_SCHEMA", default='http'),
        'netloc': '{}:{}'.format(
                    env('IGL_MESSAGEAPI_HOST', default='intergov_message_api'),
                    env('IGL_MESSAGEAPPI_PORT', default='5101')),
        'pathes': {
            'post': {
                'message': '/message'
            },
            'get': {}
        }
    },
    # simplified format
    'subscription': env(
        "IGL_SUBSCRAPI_ENDPOINT",
        default='http://subscriptions_api:5102/subscriptions'
    ),
}
