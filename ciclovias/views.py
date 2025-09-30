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
        # Show current path
        print(f"Current working directory: {os.getcwd()}")
        geojson_file_path = os.path.join("geojsons", "estacoes.geojson")
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