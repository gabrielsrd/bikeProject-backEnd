from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
import json
import os
from django.http import JsonResponse
import re
from rest_framework import status

def extract_station_id(name):
    if not isinstance(name, str):
        return None
    match = re.search(r'(\d+)', name)  # Matches any number in the string
    return int(match.group(1)) if match else None

class CicloStationsAPIView(APIView):
    def get(self, request):
        # Serve stations from the database as a GeoJSON FeatureCollection.
        # This ensures the frontend and DB share the same station ids.
        from .models import Station

        features = []
        try:
            for station in Station.objects.all():
                props = {}
                # Keep DB station_id and a prefixed name for compatibility
                props['station_id'] = station.station_id if station.station_id is not None else None
                props['original_name'] = station.name

                if props['station_id'] is not None:
                    try:
                        sid = int(props['station_id'])
                    except Exception:
                        sid = None
                else:
                    sid = None

                # Do NOT overwrite DB PK; keep external station id in properties
                # props['id'] will be set as the feature top-level id (DB PK) below

                # Make sure name is in the '123 - Name' format, but avoid double-prefixing
                if sid is not None:
                    # If DB name already starts with '<id> -', trust it
                    if isinstance(station.name, str) and station.name.strip().startswith(f"{sid} -"):
                        props['station'] = station.name
                        props['name'] = station.name
                    else:
                        props['station'] = f"{sid} - {station.name}"
                        props['name'] = props['station']
                else:
                    props['station'] = station.name
                    props['name'] = station.name

                # geometry from lat/lon
                geometry = None
                if station.longitude is not None and station.latitude is not None:
                    geometry = {
                        'type': 'Point',
                        'coordinates': [station.longitude, station.latitude]
                    }

                # add DB primary key explicitly
                props['id'] = station.id

                feature = {
                    'type': 'Feature',
                    'id': station.id,  # top-level feature id = DB PK
                    'geometry': geometry,
                    'properties': props
                }
                features.append(feature)

        except Exception as e:
            print(f"Error building stations from DB: {e}")
            return Response({"error": "Failed to load stations from DB."}, status=500)

        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }

        return JsonResponse(geojson)
    
class CicloviasAPIView(APIView):
    def get(self, request):
        # Show current path
        print(f"Current working directory: {os.getcwd()}")
        geojson_file_path = os.path.join("geojsons", "ciclovia.geojson")
        print(f"GeoJSON file path: {geojson_file_path}")

        try:
            # Open and load the GeoJSON file
            with open(geojson_file_path, "r", encoding="utf-8") as file:
                ciclovias_data = json.load(file)
        except FileNotFoundError:
            print("GeoJSON file not found.")
            return Response({"error": "GeoJSON file not found."}, status=404)
        except json.JSONDecodeError as e:
            print(f"Invalid GeoJSON format: {e}")
            return Response({"error": "Invalid GeoJSON format."}, status=400)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return Response({"error": "Internal server error."}, status=500)

        print("GeoJSON data loaded successfully.")
        return JsonResponse(ciclovias_data)
    
class HotZonesAPIView(APIView):
    def get(self, request):
        # Show current path
        print(f"Current working directory: {os.getcwd()}")
        geojson_file_path = os.path.join("geojsons", "hotzones.geojson")
        print(f"GeoJSON file path: {geojson_file_path}")

        try:
            # Open and load the GeoJSON file
            with open(geojson_file_path, "r", encoding="utf-8") as file:
                ciclovias_data = json.load(file)
        except FileNotFoundError:
            print("GeoJSON file not found.")
            return Response({"error": "GeoJSON file not found."}, status=404)
        except json.JSONDecodeError as e:
            print(f"Invalid GeoJSON format: {e}")
            return Response({"error": "Invalid GeoJSON format."}, status=400)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return Response({"error": "Internal server error."}, status=500)

        print("GeoJSON data loaded successfully.")
        return JsonResponse(ciclovias_data)

class StationsAPIView(APIView):
    def get(self, request):
        # Show current path
        print(f"Current working directory: {os.getcwd()}")
        geojson_file_path = os.path.join("geojsons", "stations.geojson")
        print(f"GeoJSON file path: {geojson_file_path}")

        try:
            # Open and load the GeoJSON file
            with open(geojson_file_path, "r", encoding="utf-8") as file:
                stations_data = json.load(file)
        except FileNotFoundError:
            print("GeoJSON file not found.")
            return Response({"error": "GeoJSON file not found."}, status=404)
        except json.JSONDecodeError as e:
            print(f"Invalid GeoJSON format: {e}")
            return Response({"error": "Invalid GeoJSON format."}, status=400)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return Response({"error": "Internal server error."}, status=500)

        print("GeoJSON data loaded successfully.")
        return JsonResponse(stations_data)

class HourlyCountsAPIView(APIView):
    def get(self, request):
        # Show current path
        print(f"Current working directory: {os.getcwd()}")
        json_file_path = os.path.join("geojsons", "hourly_counts.json")
        print(f"JSON file path: {json_file_path}")

        try:
            # Open and load the JSON file
            with open(json_file_path, "r", encoding="utf-8") as file:
                hourly_counts_data = json.load(file)
        except FileNotFoundError:
            print("JSON file not found.")
            return Response({"error": "JSON file not found."}, status=404)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON format: {e}")
            return Response({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return Response({"error": "Internal server error."}, status=500)

        print("JSON data loaded successfully.")
        return JsonResponse(hourly_counts_data, safe=False)

class StationsHistogramAPIView(APIView):
    def get(self, request):
        # Path to your CSV file (adjust as necessary)
        csv_file = "dataRaw/userTrips.csv"

        # Load the CSV file
        try:
            df = pd.read_csv(csv_file)
        except FileNotFoundError:
            return Response({"error": "CSV file not found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Convert time columns to datetime
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])

        # Extract day, hour, month, and station IDs
        df['start_day'] = df['start_time'].dt.dayofweek  # 0=Mon, 1=Tue, ..., 6=Sun
        df['end_day'] = df['end_time'].dt.dayofweek
        df['start_hour'] = df['start_time'].dt.hour
        df['end_hour'] = df['end_time'].dt.hour
        df['month'] = df['start_time'].dt.month
        df['start_station_id'] = df['initial_station_name'].apply(extract_station_id)
        df['end_station_id'] = df['final_station_name'].apply(extract_station_id)

        # query params
        selected_days = request.query_params.get('days', None) 
        exclude_months = request.query_params.get('months', None) 
        station_id = request.query_params.get('station_id', None) 
        usp = request.query_params.get('usp', None) 
        print(f"Query parameters: {request.query_params}")
        print(f"Selected days: {selected_days}")
        print(f"Excluded months: {exclude_months}")
        print(f"Station ID: {station_id}")
        print(f"USP filter: {usp}")

        # Filter by days
        if selected_days:
            try:
                selected_days = [int(day) for day in selected_days.split(',')]
                df = df[df['start_day'].isin(selected_days)]
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'days' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Default to weekdays if no days are specified
            df = df[df['start_day'] < 5]  # 0-4 are weekdays

        # Filter by excluded months
        if exclude_months:
            try:
                exclude_months = [int(month) for month in exclude_months.split(',')]
                df = df[~df['month'].isin(exclude_months)]
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'months' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter by station_id
        if station_id:
            try:
                station_id = int(station_id)
                print(f"Filtering by station_id: {station_id}")
                df = df[(df['start_station_id'] == station_id) | (df['end_station_id'] == station_id)]
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'station_id' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter by USP stations (242-260)
        if usp and usp.lower() == 'true':
            print("Applying USP filter (stations 242-260)")
            usp_range = range(242, 261) 
            df = df[
                (df['start_station_id'].isin(usp_range)) | 
                (df['end_station_id'].isin(usp_range))
            ]
            print(f"After USP filter, DataFrame size: {df.shape}")
            if df.empty:
                print("No trips found for USP stations (242-260)")

        # Process departures and arrivals
        df_departures = df
        df_arrivals = df

        # Calculate counts
        departures_counts = df_departures.groupby(['initial_station_name', 'start_day', 'start_hour']).size().reset_index(name='departures')
        arrivals_counts = df_arrivals.groupby(['final_station_name', 'end_day', 'end_hour']).size().reset_index(name='arrivals')

        # Extract station IDs
        departures_counts['station_id'] = departures_counts['initial_station_name'].apply(extract_station_id)
        arrivals_counts['station_id'] = arrivals_counts['final_station_name'].apply(extract_station_id)

        # Rename columns
        departures_counts = departures_counts.rename(columns={
            'initial_station_name': 'station',
            'start_day': 'day',
            'start_hour': 'hour'
        })
        arrivals_counts = arrivals_counts.rename(columns={
            'final_station_name': 'station',
            'end_day': 'day',
            'end_hour': 'hour'
        })

        #Merge
        histogram_data = pd.merge(departures_counts, arrivals_counts, on=['station_id', 'day', 'hour'], how='outer').fillna(0)
        histogram_data['station'] = histogram_data['station_x'].combine_first(histogram_data['station_y'])
        histogram_data = histogram_data[['station_id', 'station', 'day', 'hour', 'departures', 'arrivals']]

        # Convert to JSON format
        histogram_json = histogram_data.to_dict(orient='records')

        return Response(histogram_json, status=status.HTTP_200_OK)

class StationsHistogramDBAPIView(APIView):
    """
    Database-powered version of StationsHistogramAPIView for testing
    This should return identical results to the CSV version
    """
    def get(self, request):
        from django.db.models import Count, Q, Min, Max
        from django.db.models import F
        from .models import Trip
        
        # Get query parameters (identical to CSV version)
        selected_days = request.query_params.get('days', None) 
        exclude_months = request.query_params.get('months', None) 
        station_id = request.query_params.get('station_id', None) 
        usp = request.query_params.get('usp', None) 
        
        # Aggregation mode: 'avg' (default) or 'total'
        aggregation = request.query_params.get('aggregation', 'avg')
        aggregation = aggregation.lower() if isinstance(aggregation, str) else 'avg'

        print(f"DB Query parameters: {request.query_params}")
        print(f"Selected days: {selected_days}")
        print(f"Excluded months: {exclude_months}")
        print(f"Station ID: {station_id}")
        print(f"USP filter: {usp}")
        print(f"Aggregation mode: {aggregation}")
        
        # Start with all trips
        queryset = Trip.objects.all()
        
        # Filter by days
        if selected_days:
            try:
                selected_days = [int(day) for day in selected_days.split(',')]
                queryset = queryset.filter(start_day__in=selected_days)
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'days' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Default to weekdays if no days are specified
            queryset = queryset.filter(start_day__lt=5)  # 0-4 are weekdays
        
        # Filter by excluded months
        if exclude_months:
            try:
                exclude_months = [int(month) for month in exclude_months.split(',')]
                queryset = queryset.exclude(month__in=exclude_months)
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'months' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter by station_id (external station identifier stored on Station.station_id)
        if station_id:
            try:
                station_id = int(station_id)
                print(f"Filtering by station_id: {station_id}")
                # filter trips where the related Station.station_id matches
                queryset = queryset.filter(
                    Q(initial_station__station_id=station_id) | 
                    Q(final_station__station_id=station_id)
                )
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'station_id' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter by USP stations (242-260)
        if usp and usp.lower() == 'true':
            print("Applying USP filter (stations 242-260)")
            usp_range = range(242, 261)
            queryset = queryset.filter(
                Q(initial_station_id__in=usp_range) | 
                Q(final_station_id__in=usp_range)
            )
            print(f"After USP filter, queryset count: {queryset.count()}")
        
        # Compute period (min start_time / max end_time) per station using external station_id
        period_map = {}
        # initial station periods (use Station.station_id via relation)
        initial_periods = queryset.values('initial_station__station_id').annotate(start_min=Min('start_time'), end_max=Max('end_time'))
        for p in initial_periods:
            sid = p.get('initial_station__station_id')
            if sid is None:
                continue
            period_map[sid] = {
                'start': p.get('start_min'),
                'end': p.get('end_max')
            }
        # final station periods (merge with initial)
        final_periods = queryset.values('final_station__station_id').annotate(start_min=Min('start_time'), end_max=Max('end_time'))
        for p in final_periods:
            sid = p.get('final_station__station_id')
            if sid is None:
                continue
            if sid in period_map:
                existing = period_map[sid]
                if p.get('start_min') and (existing['start'] is None or p.get('start_min') < existing['start']):
                    existing['start'] = p.get('start_min')
                if p.get('end_max') and (existing['end'] is None or p.get('end_max') > existing['end']):
                    existing['end'] = p.get('end_max')
            else:
                period_map[sid] = {
                    'start': p.get('start_min'),
                    'end': p.get('end_max')
                }

        # Get departures data and expose external station id (Station.station_id)
        departures = queryset.annotate(initial_station_ext_id=F('initial_station__station_id')).values(
            'initial_station_name',
            'initial_station_ext_id',
            'start_day',
            'start_hour'
        ).annotate(departures=Count('id'))

        # Get arrivals data and expose external station id
        arrivals = queryset.annotate(final_station_ext_id=F('final_station__station_id')).values(
            'final_station_name',
            'final_station_ext_id',
            'end_day',
            'end_hour'
        ).annotate(arrivals=Count('id'))
        
        # Produce a compact, aggregated representation per station with 24-hour
        # arrays for departures and arrivals. The arrays contain the average
        # number of trips per hour across the selected days (or default 5
        # weekdays when no 'days' filter was provided). This yields a small
        # JSON payload that the frontend can render immediately.

        # Determine divisor for averaging: number of selected days (or 5 by default)
        if selected_days:
            try:
                days_count = len(selected_days)
            except Exception:
                days_count = 5
        else:
            days_count = 5

        # Build a map keyed by station_id
        stations_map = {}

        # Process departures: aggregate counts per station and hour
        for item in departures:
            station_id_val = item.get('initial_station_ext_id')
            station_name = item.get('initial_station_name')
            if station_id_val is None:
                station_id_val = extract_station_id(station_name)

            if station_id_val not in stations_map:
                stations_map[station_id_val] = {
                    'station_id': station_id_val,
                    'station': station_name,
                    'departures': [0] * 24,
                    'arrivals': [0] * 24
                }

            hour = item.get('start_hour')
            count = item.get('departures', 0) or 0
            if hour is not None and 0 <= hour < 24:
                stations_map[station_id_val]['departures'][hour] += count

        # Process arrivals: aggregate counts per station and hour
        for item in arrivals:
            station_id_val = item.get('final_station_ext_id')
            station_name = item.get('final_station_name')
            if station_id_val is None:
                station_id_val = extract_station_id(station_name)

            if station_id_val not in stations_map:
                stations_map[station_id_val] = {
                    'station_id': station_id_val,
                    'station': station_name,
                    'departures': [0] * 24,
                    'arrivals': [0] * 24
                }

            hour = item.get('end_hour')
            count = item.get('arrivals', 0) or 0
            if hour is not None and 0 <= hour < 24:
                stations_map[station_id_val]['arrivals'][hour] += count

        # Convert raw counts to averages per hour over the chosen days_count
        # If aggregation == 'total' we keep totals; if 'avg' we divide by days_count.
        result = []
        for sid, entry in stations_map.items():
            if aggregation == 'total':
                dep_vals = [int(c) for c in entry['departures']]
                arr_vals = [int(c) for c in entry['arrivals']]
            else:
                # default to avg
                dep_vals = [round(c / days_count, 3) for c in entry['departures']]
                arr_vals = [round(c / days_count, 3) for c in entry['arrivals']]

            period_info = period_map.get(sid) if 'period_map' in locals() else None
            period_start = period_info['start'].isoformat() if period_info and period_info.get('start') else None
            period_end = period_info['end'].isoformat() if period_info and period_info.get('end') else None

            result.append({
                'station_id': entry['station_id'],
                'station': entry['station'],
                'departures': dep_vals,
                'arrivals': arr_vals,
                'period_start': period_start,
                'period_end': period_end
            })

        # Sort result by station_id for stable output
        result.sort(key=lambda x: (x['station_id'] or 0))

        print(f"DB version returning aggregated payload for {len(result)} stations (days_count={days_count})")
        return Response(result, status=status.HTTP_200_OK)