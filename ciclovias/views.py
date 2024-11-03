from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

class CicloviasAPIView(APIView):
    def get(self, request):
        ciclovias_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-46.625290, -23.533773]
                    },
                    "properties": {
                        "name": "Ciclovia 1",
                        "description": "Descrição da Ciclovia 1"
                    }
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-46.620290, -23.530773]
                    },
                    "properties": {
                        "name": "Ciclovia 2",
                        "description": "Descrição da Ciclovia 2"
                    }
                }
            ]
        }
        return Response(ciclovias_data)
