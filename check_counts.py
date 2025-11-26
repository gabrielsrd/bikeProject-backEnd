import os
import sys
import django
from django.db.models import Q

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from ciclovias.models import Station, Trip

usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
estacoes_usp = Station.objects.filter(id__in=usp_pks)

starts_usp = Trip.objects.filter(initial_station__in=estacoes_usp).count()
ends_usp = Trip.objects.filter(final_station__in=estacoes_usp).count()
internal_usp = Trip.objects.filter(initial_station__in=estacoes_usp, final_station__in=estacoes_usp).count()
any_usp = Trip.objects.filter(Q(initial_station__in=estacoes_usp) | Q(final_station__in=estacoes_usp)).count()

print(f"Starts in USP: {starts_usp}")
print(f"Ends in USP: {ends_usp}")
print(f"Internal (USP->USP): {internal_usp}")
print(f"Any USP (Start OR End): {any_usp}")
print(f"Sum of Starts + Ends (Double counting internal): {starts_usp + ends_usp}")
