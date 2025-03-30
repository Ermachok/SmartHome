from django.shortcuts import render
from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Light, Camera
from miio import Yeelight

try:
    LAMP_IP = settings.LAMP_IP
    LAMP_TOKEN = settings.LAMP_TOKEN

    lamp = Yeelight(LAMP_IP, LAMP_TOKEN)
except Exception as e:
    lamp = None


@api_view(['POST'])
def toggle_light(request):
    """ Включает/выключает свет Xiaomi Mi Bedside Lamp 2 """
    if lamp:
        lamp.toggle()
        light = Light.objects.first()
        if not light:
            light = Light.objects.create()
        light.is_on = not light.is_on
        light.save()
        return Response({"status": "on" if light.is_on else "off"})
    return Response({"status": "error", "message": "Не удалось подключиться к лампе"}, status=500)


@api_view(['POST'])
def set_brightness(request):
    """ Устанавливает яркость (0-100) """
    brightness = int(request.data.get("brightness", 50))
    if lamp:
        lamp.set_brightness(brightness)
        return Response({"status": "success", "brightness": brightness})
    return Response({"status": "error", "message": "Не удалось изменить яркость"}, status=500)


@api_view(['POST'])
def set_color(request):
    """ Изменяет цвет лампы (RGB) """
    r = int(request.data.get("r", 255))
    g = int(request.data.get("g", 255))
    b = int(request.data.get("b", 255))
    if lamp:
        lamp.set_rgb([r, g, b])
        return Response({"status": "success", "color": f"({r}, {g}, {b})"})
    return Response({"status": "error", "message": "Не удалось изменить цвет"}, status=500)


@api_view(['POST'])
def take_photo(request):
    """ Заглушка для снимка с камеры """
    return Response({"status": "photo taken (mock)"})
