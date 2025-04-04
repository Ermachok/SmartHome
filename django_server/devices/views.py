from django.conf import settings
from miio import Yeelight
from rest_framework import status
from django.apps import apps
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import take_photo as make_photo

from .models import Camera, Light, LightSchedule
from .serializers import LightScheduleSerializer

try:
    LAMP_IP = settings.LAMP_IP
    LAMP_TOKEN = settings.LAMP_TOKEN

    lamp = Yeelight(LAMP_IP, LAMP_TOKEN)
except Exception as e:
    lamp = None


@api_view(["POST"])
def toggle_light(request):
    """Проверяет текущее состояние лампы, затем включает/выключает её"""
    try:
        is_on = lamp.status().is_on
    except Exception as e:
        return Response(
            {"status": "error", "message": f"Ошибка связи с лампой: {e}"}, status=500
        )

    lamp.toggle()
    light = Light.objects.first()
    if not light:
        light = Light.objects.create()

    light.is_on = not is_on
    light.save()

    return Response({"status": "on" if light.is_on else "off"})


@api_view(["POST"])
def set_brightness(request):
    """Устанавливает яркость (0-100)"""
    brightness = int(request.data.get("brightness", 50))
    if lamp:
        lamp.set_brightness(brightness)
        return Response({"status": "success", "brightness": brightness})
    return Response(
        {"status": "error", "message": "Не удалось изменить яркость"}, status=500
    )


@api_view(["POST"])
def set_color(request):
    """Изменяет цвет лампы (RGB)"""
    r = int(request.data.get("r", 255))
    g = int(request.data.get("g", 255))
    b = int(request.data.get("b", 255))
    if lamp:
        lamp.set_rgb((r, g, b))
        return Response({"status": "success", "color": f"({r}, {g}, {b})"})
    return Response(
        {"status": "error", "message": "Не удалось изменить цвет"}, status=500
    )


class ScheduleView(APIView):
    def get(self, request):
        """Возвращает текущее расписание."""
        schedule = LightSchedule.objects.all()
        serializer = LightScheduleSerializer(schedule, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Создает новое расписание."""
        serializer = LightScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """Удаляет расписание по ID."""
        schedule_id = request.data.get("id")
        if not schedule_id:
            return Response(
                {"error": "ID обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            schedule = LightSchedule.objects.get(id=schedule_id)
            schedule.delete()
            return Response(
                {"message": "Расписание удалено"}, status=status.HTTP_204_NO_CONTENT
            )
        except LightSchedule.DoesNotExist:
            return Response(
                {"error": "Расписание не найдено"}, status=status.HTTP_404_NOT_FOUND
            )

@csrf_exempt
@api_view(["POST"])
def take_photo(request):
    photo_path = make_photo()

    if not photo_path:
        return Response({"status": "error", "message": "Не удалось сделать фото"})

    camera = apps.get_model("devices", "Camera").objects.get(id=1)

    photo_url = request.build_absolute_uri(settings.MEDIA_URL + camera.last_photo.name)

    return Response({"status": "success", "photo_url": photo_url}, status=200)
