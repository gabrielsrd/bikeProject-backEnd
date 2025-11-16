from django.urls import path
from .views import CicloStationsAPIView, CicloviasAPIView, HotZonesAPIView, StationsAPIView, HourlyCountsAPIView, StationsHistogramAPIView, StationsHistogramDBAPIView, TripFlowsAPIView, StationTideEffectAPIView

urlpatterns = [
    path('ciclostation/', CicloStationsAPIView.as_view(), name='ciclostation'),
    path('ciclovias/', CicloviasAPIView.as_view(), name='ciclovias'),
    path('hotzones/', HotZonesAPIView.as_view(), name='hotzones'),
    path('stations/', StationsAPIView.as_view(), name='stations'),
    path('hourly_counts/', HourlyCountsAPIView.as_view(), name='hourly_counts'),
    path('station_histogram/', StationsHistogramAPIView.as_view(), name='station_histogram'),
    path('station_histogram_test/', StationsHistogramDBAPIView.as_view(), name='station_histogram_test'),
    path('trip_flows/', TripFlowsAPIView.as_view(), name='trip_flows'),
    path('station_tide_effect/', StationTideEffectAPIView.as_view(), name='station_tide_effect'),
    
]
