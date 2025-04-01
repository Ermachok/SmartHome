from rest_framework import serializers
from .models import LightSchedule

class LightScheduleSerializer(serializers.ModelSerializer):
    days = serializers.ListField(
        child=serializers.CharField(max_length=3),  \
        required=True
    )

    class Meta:
        model = LightSchedule
        fields = "__all__"

    def create(self, validated_data):
        return super().create(validated_data)
