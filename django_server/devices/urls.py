from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from .views import ScheduleView, set_brightness, set_color, take_photo, toggle_light

urlpatterns = [
    path("light/toggle/", toggle_light, name="toggle_light"),
    path("light/brightness/", set_brightness, name="set_brightness"),
    path("light/color/", set_color, name="set_color"),
    path("light/schedule/", ScheduleView.as_view(), name="light_schedule"),
    path("photo/", take_photo, name="take_photo"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
