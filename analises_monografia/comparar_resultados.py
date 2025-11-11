#!/usr/bin/env python3
"""
Comparação de Resultados - Dataset Parcial vs Completo

Compara os resultados das análises entre o dataset antigo e o novo.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from ciclovias.models import Trip, Station

def print_section(title):
    """Imprime seção formatada"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def main():
    print("\n" + "="*80)
    print("📊 COMPARAÇÃO: Dataset Parcial → Dataset Completo")
    print("="*80)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Estatísticas do banco atual
    print_section("📈 ESTATÍSTICAS DO BANCO DE DADOS ATUAL")
    
    total_trips = Trip.objects.count()
    total_stations = Station.objects.count()
    
    print(f"\nTotal de viagens:  {total_trips:,}")
    print(f"Total de estações: {total_stations:,}")
    
    if total_trips > 0:
        # Período
        first_trip = Trip.objects.order_by('start_time').first()
        last_trip = Trip.objects.order_by('-start_time').first()
        
        print(f"\nPeríodo coberto:")
        print(f"  Primeira viagem: {first_trip.start_time.strftime('%Y-%m-%d')}")
        print(f"  Última viagem:   {last_trip.start_time.strftime('%Y-%m-%d')}")
        print(f"  Duração:         {(last_trip.start_time - first_trip.start_time).days} dias")
        
        # Viagens por ano
        print("\nViagens por ano:")
        years = {}
        for year in range(2018, 2024):
            count = Trip.objects.filter(start_time__year=year).count()
            if count > 0:
                years[year] = count
                print(f"  {year}: {count:>10,} viagens")
        
        # Comparação com expectativa
        print_section("🎯 COMPARAÇÃO COM EXPECTATIVA")
        
        expected_total = 23_000_000  # Estimativa do dataset completo
        coverage_pct = (total_trips / expected_total) * 100 if expected_total > 0 else 0
        
        print(f"\nExpectativa (dataset completo):  {expected_total:>12,} viagens")
        print(f"Atual (banco db.sqlite3):        {total_trips:>12,} viagens")
        print(f"Cobertura:                       {coverage_pct:>12.1f}%")
        
        if coverage_pct >= 95:
            print("\n✅ EXCELENTE! Dataset praticamente completo!")
        elif coverage_pct >= 75:
            print("\n✓ BOM! Maioria dos dados importados")
        elif coverage_pct >= 50:
            print("\n⚠️  PARCIAL - Aproximadamente metade dos dados")
        else:
            print("\n❌ BAIXA COBERTURA - Verificar importação")
        
        # Anos faltando
        print("\nCobertura temporal:")
        for year in range(2018, 2024):
            count = years.get(year, 0)
            if count > 0:
                print(f"  {year}: ✓ Presente ({count:,} viagens)")
            else:
                print(f"  {year}: ✗ Ausente")
        
        # Meses de 2022
        print("\nDetalhamento 2022:")
        for month in range(1, 13):
            count = Trip.objects.filter(start_time__year=2022, start_time__month=month).count()
            month_name = datetime(2022, month, 1).strftime('%B')
            if count > 0:
                print(f"  {month_name:>10}: {count:>8,} viagens")
            else:
                print(f"  {month_name:>10}: ─────── (vazio)")
        
        # Estatísticas das análises
        print_section("📁 ARQUIVOS DE RESULTADOS GERADOS")
        
        resultados_dir = BASE_DIR / "analises_monografia" / "resultados"
        if resultados_dir.exists():
            csv_files = list(resultados_dir.glob("*.csv"))
            txt_files = list(resultados_dir.glob("*.txt"))
            tex_files = list(resultados_dir.glob("*.tex"))
            
            print(f"\nCSVs gerados:  {len(csv_files)}")
            for csv_file in sorted(csv_files)[:10]:  # Primeiros 10
                size_kb = csv_file.stat().st_size / 1024
                print(f"  • {csv_file.name} ({size_kb:.1f} KB)")
            
            if txt_files:
                print(f"\nRelatórios TXT: {len(txt_files)}")
                for txt_file in txt_files:
                    size_kb = txt_file.stat().st_size / 1024
                    print(f"  • {txt_file.name} ({size_kb:.1f} KB)")
            
            if tex_files:
                print(f"\nArquivos LaTeX: {len(tex_files)}")
                for tex_file in tex_files:
                    size_kb = tex_file.stat().st_size / 1024
                    print(f"  • {tex_file.name} ({size_kb:.1f} KB)")
            
            # Gráficos
            graficos_dir = resultados_dir / "graficos"
            if graficos_dir.exists():
                png_files = list(graficos_dir.glob("*.png"))
                print(f"\nGráficos PNG:  {len(png_files)}")
                for png_file in sorted(png_files)[:10]:  # Primeiros 10
                    size_kb = png_file.stat().st_size / 1024
                    print(f"  • {png_file.name} ({size_kb:.1f} KB)")
        else:
            print("\n⚠️  Pasta de resultados não encontrada")
            print("   Execute: ./analises_monografia/executar_todas_analises.sh")
        
        print_section("📋 PRÓXIMOS PASSOS")
        
        print("""
1. Verificar gráficos gerados:
   cd analises_monografia/resultados/graficos
   
2. Copiar estatísticas para monografia:
   # O arquivo estatisticas_monografia.tex contém comandos LaTeX
   # com todos os números atualizados
   
3. Atualizar texto da monografia:
   # Use os comandos \\totalViagens, \\periodoInicial, etc.
   # ao invés de números hardcoded
   
4. Se necessário, reprocessar análises específicas:
   python3 analises_monografia/02_analise_temporal.py
   python3 analises_monografia/03_analise_por_estacao.py
   python3 analises_monografia/04_analise_fluxos.py
""")
    
    else:
        print("\n❌ ERRO: Banco de dados vazio!")
        print("\nExecute:")
        print("  python3 scripts/import_to_sqlite_COMPLETO.py")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
