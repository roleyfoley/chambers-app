from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from .views import (
    CertificateViewSet, CertStatusPatchView,
    DocumentUploadView, DocumentDetailsView,
)

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'certificate', CertificateViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
app_name = "exporter-api-v0"
urlpatterns = [
    url(r'^', include(router.urls)),
    path(
        "certificate/<uuid:pk>/status/",
        view=CertStatusPatchView.as_view(),
        name="cert-status-patch"
    ),
    path(
        "certificate/<uuid:pk>/document/",
        view=DocumentUploadView.as_view(),
        name="cert-document-post"
    ),
    path(
        "certificate/<uuid:pk>/document/<uuid:docpk>/",
        view=DocumentDetailsView.as_view(),
        name="cert-document-details"
    ),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
