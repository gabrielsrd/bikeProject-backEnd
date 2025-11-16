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
from django.db.models import F

def extract_station_id(name):
    if not isinstance(name, str):
        return None
    match = re.search(r'(\d+)', name)  # Matches any number in the string
    return int(match.group(1)) if match else None

class CicloStationsAPIView(APIView):
    def get(self, request):
        # retorna estacoes do banco como GeoJSON
        from .models import Station

        features = []
        try:
            for station in Station.objects.all():
                props = {}
                props['station_id'] = station.station_id if station.station_id is not None else None
                props['original_name'] = station.name

                if props['station_id'] is not None:
                    try:
                        sid = int(props['station_id'])
                    except Exception:
                        sid = None
                else:
                    sid = None

                # formatar nome com ID
                if sid is not None:
                    if isinstance(station.name, str) and station.name.strip().startswith(f"{sid} -"):
                        props['station'] = station.name
                        props['name'] = station.name
                    else:
                        props['station'] = f"{sid} - {station.name}"
                        props['name'] = props['station']
                else:
                    props['station'] = station.name
                    props['name'] = station.name

                # geometry
                geometry = None
                if station.longitude is not None and station.latitude is not None:
                    geometry = {
                        'type': 'Point',
                        'coordinates': [station.longitude, station.latitude]
                    }

                props['id'] = station.id

                feature = {
                    'type': 'Feature',
                    'id': station.id,
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
        print(f"Diretorio: {os.getcwd()}")
        geojson_file_path = os.path.join("geojsons", "ciclovia.geojson")
        print(f"Arquivo: {geojson_file_path}")

        try:
            with open(geojson_file_path, "r", encoding="utf-8") as file:
                ciclovias_data = json.load(file)
        except FileNotFoundError:
            print("Arquivo nao encontrado")
            return Response({"error": "GeoJSON file not found."}, status=404)
        except json.JSONDecodeError as e:
            print(f"Erro no JSON: {e}")
            return Response({"error": "Invalid GeoJSON format."}, status=400)
        except Exception as e:
            print(f"Erro: {e}")
            return Response({"error": "Internal server error."}, status=500)

        print("ok")
        return JsonResponse(ciclovias_data)
    
class HotZonesAPIView(APIView):
    def get(self, request):
        geojson_file_path = os.path.join("geojsons", "hotzones.geojson")

        try:
            with open(geojson_file_path, "r", encoding="utf-8") as file:
                ciclovias_data = json.load(file)
        except FileNotFoundError:
            return Response({"error": "GeoJSON file not found."}, status=404)
        except json.JSONDecodeError as e:
            return Response({"error": "Invalid GeoJSON format."}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=500)

        return JsonResponse(ciclovias_data)

class StationsAPIView(APIView):
    def get(self, request):
        geojson_file_path = os.path.join("geojsons", "stations.geojson")

        try:
            with open(geojson_file_path, "r", encoding="utf-8") as file:
                stations_data = json.load(file)
        except FileNotFoundError:
            return Response({"error": "GeoJSON file not found."}, status=404)
        except json.JSONDecodeError as e:
            return Response({"error": "Invalid GeoJSON format."}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=500)

        return JsonResponse(stations_data)

class HourlyCountsAPIView(APIView):
    def get(self, request):
        json_file_path = os.path.join("geojsons", "hourly_counts.json")

        try:
            with open(json_file_path, "r", encoding="utf-8") as file:
                hourly_counts_data = json.load(file)
        except FileNotFoundError:
            return Response({"error": "JSON file not found."}, status=404)
        except json.JSONDecodeError as e:
            return Response({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=500)

        return JsonResponse(hourly_counts_data, safe=False)

class StationsHistogramAPIView(APIView):
    def get(self, request):
        csv_file = "dataRaw/userTrips.csv"

        try:
            df = pd.read_csv(csv_file)
        except FileNotFoundError:
            return Response({"error": "CSV file not found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])

        df['start_day'] = df['start_time'].dt.dayofweek
        df['end_day'] = df['end_time'].dt.dayofweek
        df['start_hour'] = df['start_time'].dt.hour
        df['end_hour'] = df['end_time'].dt.hour
        df['month'] = df['start_time'].dt.month
        df['start_station_id'] = df['initial_station_name'].apply(extract_station_id)
        df['end_station_id'] = df['final_station_name'].apply(extract_station_id)

        # parametros
        selected_days = request.query_params.get('days', None) 
        exclude_months = request.query_params.get('months', None) 
        station_id = request.query_params.get('station_id', None) 
        usp = request.query_params.get('usp', None)

        # filtrar por dias
        if selected_days:
            try:
                selected_days = [int(day) for day in selected_days.split(',')]
                df = df[df['start_day'].isin(selected_days)]
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'days' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            df = df[df['start_day'] < 5]

        # filtrar meses
        if exclude_months:
            try:
                exclude_months = [int(month) for month in exclude_months.split(',')]
                df = df[~df['month'].isin(exclude_months)]
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'months' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        # filtrar estacao
        if station_id:
            try:
                station_id = int(station_id)
                df = df[(df['start_station_id'] == station_id) | (df['end_station_id'] == station_id)]
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'station_id' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        # filtro USP
        if usp and usp.lower() == 'true':
            usp_range = range(242, 261) 
            df = df[
                (df['start_station_id'].isin(usp_range)) | 
                (df['end_station_id'].isin(usp_range))
            ]

        df_departures = df
        df_arrivals = df

        departures_counts = df_departures.groupby(['initial_station_name', 'start_day', 'start_hour']).size().reset_index(name='departures')
        arrivals_counts = df_arrivals.groupby(['final_station_name', 'end_day', 'end_hour']).size().reset_index(name='arrivals')

        departures_counts['station_id'] = departures_counts['initial_station_name'].apply(extract_station_id)
        arrivals_counts['station_id'] = arrivals_counts['final_station_name'].apply(extract_station_id)

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

        histogram_data = pd.merge(departures_counts, arrivals_counts, on=['station_id', 'day', 'hour'], how='outer').fillna(0)
        histogram_data['station'] = histogram_data['station_x'].combine_first(histogram_data['station_y'])
        histogram_data = histogram_data[['station_id', 'station', 'day', 'hour', 'departures', 'arrivals']]

        histogram_json = histogram_data.to_dict(orient='records')

        return Response(histogram_json, status=status.HTTP_200_OK)

class StationsHistogramDBAPIView(APIView):
    # versao usando banco de dados
    def get(self, request):
        from django.db.models import Count, Q, Min, Max
        from django.db.models import F
        from .models import Trip
        
        selected_days = request.query_params.get('days', None) 
        exclude_months = request.query_params.get('months', None) 
        station_id = request.query_params.get('station_id', None)
        station_pk = request.query_params.get('id', None)
        usp = request.query_params.get('usp', None) 
        
        aggregation = request.query_params.get('aggregation', 'avg')
        aggregation = aggregation.lower() if isinstance(aggregation, str) else 'avg'
        
        # se station_id parece ser PK, usar como PK
        if station_id and not station_pk:
            try:
                sid = int(station_id)
                if sid > 1000:
                    station_pk = station_id
                    station_id = None
            except (ValueError, TypeError):
                pass
        
        queryset = Trip.objects.all()
        
        # filtros
        if selected_days:
            try:
                selected_days = [int(day) for day in selected_days.split(',')]
                queryset = queryset.filter(start_day__in=selected_days)
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'days' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            queryset = queryset.filter(start_day__lt=5)
        
        if exclude_months:
            try:
                exclude_months = [int(month) for month in exclude_months.split(',')]
                queryset = queryset.exclude(month__in=exclude_months)
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'months' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        filter_station_id_value = None
        
        if station_pk:
            try:
                station_pk = int(station_pk)
                queryset = queryset.filter(
                    Q(initial_station_id=station_pk) | 
                    Q(final_station_id=station_pk)
                )
                
                from .models import Station
                try:
                    station_obj = Station.objects.get(id=station_pk)
                    filter_station_id_value = station_obj.station_id
                except Station.DoesNotExist:
                    pass
                    
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'id' parameter"}, status=status.HTTP_400_BAD_REQUEST)
                
        elif station_id:
            try:
                station_id = int(station_id)
                filter_station_id_value = station_id
                queryset = queryset.filter(
                    Q(initial_station__station_id=station_id) | 
                    Q(final_station__station_id=station_id)
                )
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'station_id' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        if usp and usp.lower() == 'true':
            usp_range = range(242, 261)
            queryset = queryset.filter(
                Q(initial_station__station_id__in=usp_range) | 
                Q(final_station__station_id__in=usp_range)
            )
        
        period_map = {}
        
        if station_pk or station_id:
            use_id = filter_station_id_value
            
            if station_pk:
                period_query = queryset.aggregate(start_min=Min('start_time'), end_max=Max('end_time'))
            else:
                period_query = queryset.filter(
                    Q(initial_station__station_id=use_id) | 
                    Q(final_station__station_id=use_id)
                ).aggregate(start_min=Min('start_time'), end_max=Max('end_time'))
            
            if use_id:
                period_map[use_id] = {
                    'start': period_query.get('start_min'),
                    'end': period_query.get('end_max')
                }
            
            if station_pk:
                departures = queryset.filter(
                    initial_station_id=station_pk
                ).values(
                    'initial_station_name',
                    'initial_station__station_id',
                    'start_hour'
                ).annotate(departures=Count('id'))
                
                arrivals = queryset.filter(
                    final_station_id=station_pk
                ).values(
                    'final_station_name',
                    'final_station__station_id',
                    'end_hour'
                ).annotate(arrivals=Count('id'))
            else:
                departures = queryset.filter(
                    initial_station__station_id=use_id
                ).values(
                    'initial_station_name',
                    'initial_station__station_id',
                    'start_hour'
                ).annotate(departures=Count('id'))
                
                arrivals = queryset.filter(
                    final_station__station_id=use_id
                ).values(
                    'final_station_name',
                    'final_station__station_id',
                    'end_hour'
                ).annotate(arrivals=Count('id'))
            
        else:
            # todas as estacoes
            initial_periods = queryset.values('initial_station__station_id').annotate(
                start_min=Min('start_time'), 
                end_max=Max('end_time')
            )
            
            for p in initial_periods:
                sid = p.get('initial_station__station_id')
                if sid is None:
                    continue
                period_map[sid] = {
                    'start': p.get('start_min'),
                    'end': p.get('end_max')
                }
            
            final_periods = queryset.values('final_station__station_id').annotate(
                start_min=Min('start_time'), 
                end_max=Max('end_time')
            )
            
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

            departures = queryset.annotate(
                initial_station_ext_id=F('initial_station__station_id')
            ).values(
                'initial_station_name',
                'initial_station_ext_id',
                'start_day',
                'start_hour'
            ).annotate(departures=Count('id'))

            arrivals = queryset.annotate(
                final_station_ext_id=F('final_station__station_id')
            ).values(
                'final_station_name',
                'final_station_ext_id',
                'end_day',
                'end_hour'
            ).annotate(arrivals=Count('id'))
        
        # calc media por dia
        if selected_days:
            try:
                days_count = len(selected_days)
            except Exception:
                days_count = 5
        else:
            days_count = 5

        stations_map = {}
        
        # processar departures
        for item in departures:
            if station_pk or station_id:
                station_id_val = item.get('initial_station__station_id')
                station_name = item.get('initial_station_name')
            else:
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

        # processar arrivals
        for item in arrivals:
            if station_pk or station_id:
                station_id_val = item.get('final_station__station_id')
                station_name = item.get('final_station_name')
            else:
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

        # converter para media ou total
        result = []
        for sid, entry in stations_map.items():
            if aggregation == 'total':
                dep_vals = [int(c) for c in entry['departures']]
                arr_vals = [int(c) for c in entry['arrivals']]
            else:
                dep_vals = [round(c / days_count, 3) for c in entry['departures']]
                arr_vals = [round(c / days_count, 3) for c in entry['arrivals']]

            period_info = period_map.get(sid) if 'period_map' in locals() else None
            period_start = period_info['start'].isoformat() if period_info and period_info.get('start') else None
            period_end = period_info['end'].isoformat() if period_info and period_info.get('end') else None

            result.append({
                'station_id': station_pk,
                'station': entry['station'],
                'departures': dep_vals,
                'arrivals': arr_vals,
                'period_start': period_start,
                'period_end': period_end
            })

        result.sort(key=lambda x: (x['station_id'] or 0))

        return Response(result, status=status.HTTP_200_OK)

class TripFlowsAPIView(APIView):
    # principais fluxos entre estacoes
    def get(self, request):
        from django.db.models import Count, Q
        from .models import Trip
        
        selected_days = request.query_params.get('days', None)
        exclude_months = request.query_params.get('months', None)
        usp = request.query_params.get('usp', None)
        min_trips = int(request.query_params.get('min_trips', '10'))
        limit = int(request.query_params.get('limit', '100'))
        
        queryset = Trip.objects.all()
        
        # filtros
        if selected_days:
            try:
                selected_days = [int(day) for day in selected_days.split(',')]
                queryset = queryset.filter(start_day__in=selected_days)
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'days' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            queryset = queryset.filter(start_day__lt=5)
        
        if exclude_months:
            try:
                exclude_months = [int(month) for month in exclude_months.split(',')]
                queryset = queryset.exclude(month__in=exclude_months)
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'months' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        if usp and usp.lower() == 'true':
            usp_range = range(242, 261)
            queryset = queryset.filter(
                Q(initial_station__station_id__in=usp_range) | 
                Q(final_station__station_id__in=usp_range)
            )
        
        # agregar fluxos
        flows = queryset.exclude(
            initial_station__station_id=F('final_station__station_id')
        ).values(
            'initial_station__station_id',
            'initial_station__latitude',
            'initial_station__longitude',
            'initial_station__name',
            'final_station__station_id',
            'final_station__latitude',
            'final_station__longitude',
            'final_station__name',
        ).annotate(
            trip_count=Count('id')
        ).filter(
            trip_count__gte=min_trips,
            initial_station__isnull=False,
            final_station__isnull=False,
            initial_station__latitude__isnull=False,
            final_station__latitude__isnull=False,
            final_station__longitude__isnull=False,
            initial_station__longitude__isnull=False
        ).order_by('-trip_count')[:limit]
        
        result = []
        for flow in flows:
            result.append({
                'origin_station_id': flow['initial_station__station_id'],
                'origin_station_name': flow['initial_station__name'],
                'origin_coords': [
                    flow['initial_station__latitude'],
                    flow['initial_station__longitude']
                ],
                'destination_station_id': flow['final_station__station_id'],
                'destination_station_name': flow['final_station__name'],
                'destination_coords': [
                    flow['final_station__latitude'],
                    flow['final_station__longitude']
                ],
                'trip_count': flow['trip_count']
            })

        return Response(result, status=status.HTTP_200_OK)


class StationTideEffectAPIView(APIView):
    # efeito mare: saldo de partidas vs chegadas
    def get(self, request):
        from django.db.models import Count, Q
        from .models import Trip, Station
        
        station_id = request.query_params.get('station_id', None)
        
        if not station_id:
            return Response(
                {"error": "Parameter 'station_id' is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            station_id = int(station_id)
        except ValueError:
            return Response(
                {"error": "Invalid 'station_id' parameter"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            station = Station.objects.get(station_id=station_id)
        except Station.DoesNotExist:
            return Response(
                {"error": f"Station with id {station_id} not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        selected_days = request.query_params.get('days', None)
        exclude_months = request.query_params.get('months', None)
        start_date = request.query_params.get('startDate', None)
        end_date = request.query_params.get('endDate', None)
        
        queryset = Trip.objects.all()
        
        # filtros
        if selected_days:
            try:
                selected_days = [int(day) for day in selected_days.split(',')]
                queryset = queryset.filter(start_day__in=selected_days)
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'days' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            queryset = queryset.filter(start_day__lt=5)
        
        if exclude_months:
            try:
                exclude_months = [int(month) for month in exclude_months.split(',')]
                queryset = queryset.exclude(month__in=exclude_months)
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'months' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(start_date__lte=end_date)
        
        # partidas
        departures = queryset.filter(
            initial_station__station_id=station_id
        ).values('start_hour').annotate(
            count=Count('id')
        ).order_by('start_hour')
        
        # chegadas
        arrivals = queryset.filter(
            final_station__station_id=station_id
        ).values('start_hour').annotate(
            count=Count('id')
        ).order_by('start_hour')
        
        result = []
        departures_dict = {item['start_hour']: item['count'] for item in departures if item['start_hour'] is not None}
        arrivals_dict = {item['start_hour']: item['count'] for item in arrivals if item['start_hour'] is not None}
        
        for hour in range(24):
            dep = departures_dict.get(hour, 0)
            arr = arrivals_dict.get(hour, 0)
            balance = dep - arr
            
            result.append({
                'hour': hour,
                'departures': dep,
                'arrivals': arr,
                'balance': balance
            })
        
        response_data = {
            'station_id': station_id,
            'station_name': station.name,
            'data': result,
            'total_departures': sum(departures_dict.values()),
            'total_arrivals': sum(arrivals_dict.values()),
            'total_balance': sum(departures_dict.values()) - sum(arrivals_dict.values())
        }

        return Response(response_data, status=status.HTTP_200_OK)