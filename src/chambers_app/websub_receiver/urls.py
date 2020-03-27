from django.urls import path

from .views import (
    MsgNotificationReceiveView, CertStatusNotificationView
)

app_name = "websub_receiver"
urlpatterns = [
    path(
        "channel/messages/<str:subscr_uuid>/",
        view=MsgNotificationReceiveView.as_view(),
        name="message-event"
    ),
    path(
        "channel/cert-status-update/<str:subscr_uuid>/",
        view=CertStatusNotificationView.as_view(),
        name="certificate-status-update"
    ),
]
