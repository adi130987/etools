import json

from rest_framework import serializers

from etools.applications.hact.models import HactHistory


class HactHistorySerializer(serializers.ModelSerializer):
    partner_values = serializers.SerializerMethodField()

    def get_partner_values(self, obj):
        return json.loads(obj.partner_values) if isinstance(obj.partner_values, str) else obj.partner_values

    class Meta:
        model = HactHistory
        fields = (
            "id",
            "year",
            "created",
            "modified",
            "partner_values",
        )


class AggregateHactSerializer(serializers.ModelSerializer):
    partner_values = serializers.SerializerMethodField()

    def get_partner_values(self, obj):
        return json.loads(obj.partner_values) if isinstance(obj.partner_values, str) else obj.partner_values

    class Meta:
        model = HactHistory
        fields = (
            "id",
            "year",
            "created",
            "modified",
            "partner_values",
        )


class HactHistoryExportSerializer(serializers.BaseSerializer):
    @property
    def data(self):
        return self.to_presentation(self.initial_data)

    def to_representation(self, data):
        try:
            data = json.loads(data.partner_values)
        except (ValueError, TypeError):
            data = data.partner_values
        return [x[1] for x in data]
