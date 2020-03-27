from django.conf import settings


def misc_variables(request):
    ret = {
        'ICL_CHAMBERS_APP_HOST': settings.ICL_CHAMBERS_APP_HOST,
        'ICL_CHAMBERS_APP_COUNTRY': settings.ICL_CHAMBERS_APP_COUNTRY,
        'CSS_COUNTRY_THEME': f'css/project.{settings.CSS_COUNTRY}.css',
    }
    return ret
