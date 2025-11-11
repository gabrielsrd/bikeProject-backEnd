#!/usr/bin/env python3
"""
Importador COMPLETO para SQLite - Versão 2.0

Importa 100% do consolidated_tembici_data_COMPLETO.csv para SQLite
sem interrupções, com verificação de progresso e recuperação.

Database: db_COMPLETO.sqlite3
"""

import os
import sys
import django
import csv
import time
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('importacao_completa.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# IMPORTANTE: Configurar o banco de dados ANTES de setup()
os.environ['SQLITE_DB_NAME'] = 'db_COMPLETO.sqlite3'

django.setup()

from django.core.management import call_command
from ciclovias.models import Station, Trip
from django.db import connection

def count_csv_rows(file_path):
    """Conta linhas do CSV de forma eficiente"""
    logger.info("Contando linhas do CSV...")
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        next(f)  # Skip header
        for line in f:
            count += 1
    return count

def check_database_state():
    """Verifica estado atual do banco de dados"""
    try:
        station_count = Station.objects.count()
        trip_count = Trip.objects.count()
        
        if trip_count > 0:
            # Verificar última viagem importada
            last_trip = Trip.objects.order_by('-id').first()
            logger.info(f"""
Estado atual do banco de dados:
  • Estações: {station_count:,}
  • Viagens: {trip_count:,}
  • Última viagem ID: {last_trip.trip_id if last_trip else 'N/A'}
  • Última viagem data: {last_trip.start_time if last_trip else 'N/A'}
""")
        else:
            logger.info(f"""
Estado atual do banco de dados:
  • Estações: {station_count:,}
  • Viagens: {trip_count:,} (vazio)
""")
        
        return station_count, trip_count
        
    except Exception as e:
        logger.error(f"Erro ao verificar banco de dados: {e}")
        return 0, 0

def get_database_size():
    """Retorna tamanho do banco de dados em MB"""
    db_path = BASE_DIR / 'db_COMPLETO.sqlite3'
    if db_path.exists():
        size_mb = db_path.stat().st_size / 1024 / 1024
        return size_mb
    return 0

def optimize_database():
    """Otimiza o banco de dados SQLite"""
    logger.info("Otimizando banco de dados...")
    try:
        with connection.cursor() as cursor:
            # VACUUM para compactar
            cursor.execute('VACUUM')
            # ANALYZE para otimizar queries
            cursor.execute('ANALYZE')
        logger.info("✓ Banco de dados otimizado")
    except Exception as e:
        logger.warning(f"⚠ Erro ao otimizar: {e}")

def main():
    """Função principal"""
    
    # Banner
    print("\n" + "="*80)
    print("🗄️  IMPORTADOR COMPLETO PARA SQLITE")
    print("="*80)
    print(f"Versão: 2.0 - DATASET COMPLETO")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Banco de dados: db_COMPLETO.sqlite3")
    print("="*80 + "\n")
    
    # Verificar arquivo CSV
    csv_file = BASE_DIR / "dataRaw" / "consolidated_tembici_data_COMPLETO.csv"
    
    if not csv_file.exists():
        logger.error(f"❌ Arquivo CSV não encontrado: {csv_file}")
        logger.error("   Execute primeiro: python scripts/consolidate_tembici_COMPLETO.py")
        return
    
    csv_size_mb = csv_file.stat().st_size / 1024 / 1024
    logger.info(f"📄 Arquivo CSV encontrado: {csv_size_mb:.2f} MB")
    
    # Contar linhas do CSV
    logger.info("Verificando tamanho do dataset...")
    total_rows = count_csv_rows(csv_file)
    logger.info(f"📊 Total de viagens no CSV: {total_rows:,}")
    
    # Verificar estado do banco
    logger.info("\nVerificando estado do banco de dados...")
    station_count_before, trip_count_before = check_database_state()
    
    if trip_count_before > 0:
        logger.warning(f"\n⚠️  ATENÇÃO: Banco já contém {trip_count_before:,} viagens!")
        response = input("\nDeseja:\n  [1] Continuar importação (adicionar novos)\n  [2] Limpar e recomeçar\n  [3] Cancelar\nEscolha: ")
        
        if response == "2":
            logger.info("Limpando banco de dados...")
            Trip.objects.all().delete()
            Station.objects.all().delete()
            logger.info("✓ Banco limpo!")
            station_count_before, trip_count_before = 0, 0
        elif response == "3":
            logger.info("Importação cancelada pelo usuário")
            return
        else:
            logger.info("Continuando importação...")
    
    # Configuração da importação
    batch_size = 10000  # Batches maiores para importação mais rápida
    chunk_rows = 200000  # Chunks maiores para melhor performance
    
    logger.info(f"""
Configuração da importação:
  • Batch size: {batch_size:,} viagens por transação
  • Chunk size: {chunk_rows:,} linhas por chunk
  • Total estimado: {total_rows:,} viagens
  • Tempo estimado: ~{total_rows / 50000:.0f} minutos (a 50k viagens/min)
""")
    
    # Confirmar
    response = input("Iniciar importação? [S/n]: ")
    if response.lower() == 'n':
        logger.info("Importação cancelada")
        return
    
    # Iniciar importação
    logger.info("\n" + "="*80)
    logger.info("INICIANDO IMPORTAÇÃO")
    logger.info("="*80)
    
    start_time = time.time()
    
    try:
        # Chamar comando Django de importação
        call_command(
            'import_trips',
            str(csv_file),
            batch_size=batch_size,
            chunk_rows=chunk_rows,
            total_rows=total_rows,
            assume_tz='America/Sao_Paulo',
            verbosity=2
        )
        
        elapsed = time.time() - start_time
        
        # Verificar resultado
        logger.info("\n" + "="*80)
        logger.info("VERIFICANDO RESULTADO")
        logger.info("="*80)
        
        station_count_after, trip_count_after = check_database_state()
        
        trips_imported = trip_count_after - trip_count_before
        import_rate = trips_imported / elapsed if elapsed > 0 else 0
        
        # Estatísticas finais
        logger.info("\n" + "="*80)
        logger.info("📊 ESTATÍSTICAS FINAIS")
        logger.info("="*80)
        logger.info(f"""
DADOS IMPORTADOS:
  • Estações antes:        {station_count_before:>12,}
  • Estações depois:       {station_count_after:>12,}
  • Estações novas:        {station_count_after - station_count_before:>12,}

  • Viagens antes:         {trip_count_before:>12,}
  • Viagens depois:        {trip_count_after:>12,}
  • Viagens importadas:    {trips_imported:>12,}

DESEMPENHO:
  • Tempo total:           {int(elapsed // 60):>12} min {int(elapsed % 60):>2} seg
  • Taxa de importação:    {import_rate:>12,.0f} viagens/segundo
  • Tamanho do banco:      {get_database_size():>12,.2f} MB

COBERTURA:
  • Viagens no CSV:        {total_rows:>12,}
  • Viagens importadas:    {trips_imported:>12,}
  • Taxa de sucesso:       {trips_imported / total_rows * 100 if total_rows > 0 else 0:>12.1f}%
""")
        
        # Verificar se importou tudo
        if trips_imported < total_rows * 0.95:
            logger.warning("\n⚠️  ATENÇÃO: Importação incompleta!")
            logger.warning(f"   Faltam: {total_rows - trips_imported:,} viagens ({(total_rows - trips_imported) / total_rows * 100:.1f}%)")
            logger.warning("   Verifique os logs para detalhes")
        else:
            logger.info("\n✅ IMPORTAÇÃO COMPLETA COM SUCESSO!")
            
        # Otimizar banco
        optimize_database()
        
        logger.info("\n" + "="*80)
        logger.info("✅ IMPORTAÇÃO FINALIZADA")
        logger.info("="*80)
        logger.info(f"Banco de dados: {BASE_DIR / 'db_COMPLETO.sqlite3'}")
        logger.info(f"Total de viagens: {trip_count_after:,}")
        logger.info(f"Tamanho: {get_database_size():.2f} MB")
        logger.info("="*80 + "\n")
        
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        logger.warning("\n\n⚠️  IMPORTAÇÃO INTERROMPIDA PELO USUÁRIO!")
        logger.warning(f"   Tempo decorrido: {int(elapsed // 60)} min {int(elapsed % 60)} seg")
        
        station_count_after, trip_count_after = check_database_state()
        trips_imported = trip_count_after - trip_count_before
        
        logger.warning(f"   Viagens importadas até agora: {trips_imported:,}")
        logger.warning(f"   Progresso: {trips_imported / total_rows * 100:.1f}%")
        logger.warning("\n   Para continuar, execute o script novamente e escolha opção [1] Continuar")
        
    except Exception as e:
        logger.error(f"\n❌ ERRO DURANTE IMPORTAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        
        station_count_after, trip_count_after = check_database_state()
        trips_imported = trip_count_after - trip_count_before
        
        if trips_imported > 0:
            logger.info(f"\n   Viagens importadas antes do erro: {trips_imported:,}")
            logger.info(f"   Progresso: {trips_imported / total_rows * 100:.1f}%")

if __name__ == "__main__":
    main()
