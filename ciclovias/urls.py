from django.urls import path
from .views import CicloviasAPIView

urlpatterns = [
    path('ciclovias/', CicloviasAPIView.as_view(), name='ciclovias'),
]
