# views.py
import pandas as pd
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

def extract_station_id(name):
    match = re.match(r'(\d+)', name)
    return int(match.group(1)) if match else None

class StationsHistogramAPIView(APIView):
    def get(self, request):
        # Path to your CSV file (adjust as necessary)
        csv_file = "../dataRaw/userTrips.csv"

        # Load the CSV file
        try:
            df = pd.read_csv(csv_file)
        except FileNotFoundError:
            return Response({"error": "CSV file not found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Convert time columns to datetime
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])

        # Extract day, hour, and month
        df['start_day'] = df['start_time'].dt.dayofweek  # 0=Mon, 1=Tue, ..., 6=Sun
        df['end_day'] = df['end_time'].dt.dayofweek
        df['start_hour'] = df['start_time'].dt.hour
        df['end_hour'] = df['end_time'].dt.hour
        df['month'] = df['start_time'].dt.month

        # Get query parameters
        selected_days = request.query_params.get('days', None)  # e.g., "0,2,4" for Mon, Wed, Fri
        exclude_months = request.query_params.get('months', None)  # e.g., "6,7" for June, July

        # Convert query parameters to lists of integers
        if selected_days:
            try:
                selected_days = [int(day) for day in selected_days.split(',')]
                df = df[df['start_day'].isin(selected_days)]
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'days' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Default to weekdays if no days are specified
            df = df[df['start_day'] < 5]  # 0-4 are weekdays

        if exclude_months:
            try:
                exclude_months = [int(month) for month in exclude_months.split(',')]
                df = df[~df['month'].isin(exclude_months)]
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'months' parameter"}, status=status.HTTP_400_BAD_REQUEST)

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

        # Merge data
        histogram_data = pd.merge(departures_counts, arrivals_counts, on=['station_id', 'day', 'hour'], how='outer').fillna(0)
        histogram_data['station'] = histogram_data['station_x'].combine_first(histogram_data['station_y'])
        histogram_data = histogram_data[['station_id', 'station', 'day', 'hour', 'departures', 'arrivals']]

        # Convert to JSON-serializable format
        histogram_json = histogram_data.to_dict(orient='records')

        return Response(histogram_json, status=status.HTTP_200_OK)