from rest_framework import serializers
from .models import LightSchedule

class LightScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LightSchedule
        fields = "__all__"
