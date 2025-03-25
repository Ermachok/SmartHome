from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Light, Camera


@api_view(['POST'])
def toggle_light(request):
    """ Включает/выключает свет """
    light = Light.objects.first()
    if not light:
        light = Light.objects.create()
    light.is_on = not light.is_on
    light.save()
    return Response({"status": "on" if light.is_on else "off"})


@api_view(['POST'])
def take_photo(request):
    """ Заглушка для снимка с камеры """
    return Response({"status": "photo taken (mock)"})
