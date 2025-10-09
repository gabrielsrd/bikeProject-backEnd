from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

class Station(models.Model):
    station_id = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.station_id} - {self.name}" if self.station_id else self.name
    
    class Meta:
        indexes = [
            models.Index(fields=['station_id']),
            models.Index(fields=['name']),
        ]

class Trip(models.Model):
    trip_id = models.CharField(max_length=255, unique=True)
    duration_seconds = models.IntegerField(validators=[MinValueValidator(0)])
    
    # Station references (keeping original names for compatibility)
    initial_station_name = models.CharField(max_length=255)
    final_station_name = models.CharField(max_length=255)
    initial_station = models.ForeignKey(Station, on_delete=models.SET_NULL, 
                                      null=True, blank=True, related_name='departing_trips')
    final_station = models.ForeignKey(Station, on_delete=models.SET_NULL, 
                                    null=True, blank=True, related_name='arriving_trips')
    
    # Timestamps
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # Additional data
    birth_year = models.CharField(max_length=10, blank=True)
    
    # Coordinates (for trips without station references)
    initial_station_latitude = models.FloatField(null=True, blank=True)
    initial_station_longitude = models.FloatField(null=True, blank=True)
    final_station_latitude = models.FloatField(null=True, blank=True)
    final_station_longitude = models.FloatField(null=True, blank=True)
    
    # Computed fields for faster queries (pre-calculated from timestamps)
    start_day = models.IntegerField(null=True, blank=True)  # 0=Mon, 6=Sun
    start_hour = models.IntegerField(null=True, blank=True)
    end_day = models.IntegerField(null=True, blank=True)
    end_hour = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Trip {self.trip_id}: {self.initial_station_name} → {self.final_station_name}"
    
    class Meta:
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
            models.Index(fields=['start_day']),
            models.Index(fields=['start_hour']),
            models.Index(fields=['month']),
            models.Index(fields=['initial_station']),
            models.Index(fields=['final_station']),
            models.Index(fields=['trip_id']),
        ]
