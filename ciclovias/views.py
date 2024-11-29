from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
import json
import os
from django.http import JsonResponse


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
    