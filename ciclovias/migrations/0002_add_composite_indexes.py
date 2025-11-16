# Generated manually for performance optimization
# Date: 2025-11-15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ciclovias', '0001_initial'),
    ]

    operations = [
        # Adicionar índices compostos para otimizar queries do histograma
        # Estes índices melhoram performance de queries com múltiplos filtros
        
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(
                fields=['start_day', 'month'],
                name='trip_day_month_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(
                fields=['start_day', 'month', 'start_hour'],
                name='trip_day_month_hour_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(
                fields=['initial_station', 'start_hour'],
                name='trip_init_sta_hour_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(
                fields=['final_station', 'end_hour'],
                name='trip_final_sta_hour_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(
                fields=['end_hour'],
                name='trip_end_hour_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(
                fields=['start_time', 'end_time'],
                name='trip_time_range_idx'
            ),
        ),
        # Índice para queries de data (filtros de período)
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(
                fields=['month', 'start_day'],
                name='trip_month_day_idx'
            ),
        ),
    ]
