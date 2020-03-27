from django.urls import path

from chambers_app.certificates.views.certs import (
    CertificateListView, CertificateCreateView,
    CertificateDetailView, CertificateDocDownloadView,
)


app_name = "certificates"
urlpatterns = [
    path("certificates/", view=CertificateListView.as_view(), name="list"),
    path("certificates/create/", view=CertificateCreateView.as_view(), name="create"),
    path("certificates/<uuid:pk>/", view=CertificateDetailView.as_view(), name="detail"),
    path(
        "certificates/<uuid:pk>/documents/<uuid:doc_id>/",
        view=CertificateDocDownloadView.as_view(),
        name="document-download"
    ),
]
