from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.views import defaults as default_views

from .healthcheck import HealthcheckView

urlpatterns = [
    path("", login_required(
        TemplateView.as_view(template_name="pages/home.html")
    ), name="home"),
    path("about/", login_required(
        TemplateView.as_view(template_name="pages/about.html")
    ), name="about"),

    path("certificates/", include("chambers_app.certificates.urls", namespace="certificates")),
    path(
        "api/certificate/v0/",
        include("chambers_app.certificate_api_v0.urls", namespace="certificate-api-v0")
    ),

    path(settings.ADMIN_URL, admin.site.urls),
    path('oidc/', include('mozilla_django_oidc.urls')),

    path("users/", include("chambers_app.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    path("healthcheck", HealthcheckView.as_view()),
    path("websub/", include("chambers_app.websub_receiver.urls", namespace="websub")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
