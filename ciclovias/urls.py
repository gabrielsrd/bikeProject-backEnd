from django.urls import path
from .views import CicloStationsAPIView, CicloviasAPIView,  HotZonesAPIView

urlpatterns = [
    path('ciclostation/', CicloStationsAPIView.as_view(), name='ciclostation'),
    path('ciclovias/', CicloviasAPIView.as_view(), name='ciclovias'),
    path('hotzones/', HotZonesAPIView.as_view(), name='hotzones'),
]
