from rest_framework import serializers


class WebhookReceiveSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=100)
    event_type = serializers.CharField(required=False, allow_blank=True)
    payload = serializers.JSONField(required=False)

    def validate(self, attrs):
        if "payload" not in attrs:
            attrs["payload"] = dict(self.initial_data)

        attrs["event_type"] = attrs.get("event_type") or "UNKNOWN"
        return attrs