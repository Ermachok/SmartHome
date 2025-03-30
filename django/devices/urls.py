from django.urls import path
from .views import toggle_light, take_photo, set_brightness, set_color

urlpatterns = [
    path("light/toggle/", toggle_light, name="toggle_light"),
    path("light/brightness/", set_brightness, name="set_brightness"),
    path("light/color/", set_color, name="set_color"),
    path("photo/", take_photo, name="take_photo"),
]