from django.urls import path
from .views import toggle_light, take_photo

urlpatterns = [
    path('light/toggle/', toggle_light, name='toggle_light'),
    path('camera/photo/', take_photo, name='take_photo'),
]
