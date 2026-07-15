from django.urls import path

from apps.webhooks.views import GatewayWebhookView

urlpatterns = [
    path("gateway/", GatewayWebhookView.as_view(), name="gateway-webhook"),
]