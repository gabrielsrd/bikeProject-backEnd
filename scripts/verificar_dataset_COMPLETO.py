#!/usr/bin/env python3
"""
Script de Verificação do Dataset COMPLETO

Compara:
1. consolidated_tembici_data.csv (atual, parcial)
2. consolidated_tembici_data_COMPLETO.csv (novo, completo)
3. db.sqlite3 (banco atual)
4. db_COMPLETO.sqlite3 (banco novo)
"""

import os
import sys
import csv
from pathlib import Path
from datetime import datetime
import django

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from ciclovias.models import Trip

def count_csv_lines(filepath):
    """Conta linhas de um CSV"""
    if not filepath.exists():
        return 0
    
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        next(f)  # Skip header
        for _ in f:
            count += 1
    return count

def get_csv_date_range(filepath, sample_size=10000):
    """Obtém range de datas de um CSV (amostragem)"""
    if not filepath.exists():
        return None, None
    
    dates = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= sample_size:
                break
            start_time = row.get('start_time', '')
            if start_time:
                try:
                    # Extrair apenas YYYY-MM
                    year_month = start_time[:7]  # 2020-01
                    if year_month not in dates:
                        dates.append(year_month)
                except:
                    pass
    
    if dates:
        dates.sort()
        return dates[0], dates[-1]
    return None, None

def analyze_csv(filepath, name):
    """Analisa um arquivo CSV"""
    print(f"\n{'='*80}")
    print(f"📄 {name}")
    print(f"{'='*80}")
    
    if not filepath.exists():
        print(f"   ❌ Arquivo não encontrado: {filepath}")
        return {
            'exists': False,
            'count': 0,
            'size_mb': 0,
            'date_range': (None, None)
        }
    
    # Tamanho
    size_mb = filepath.stat().st_size / 1024 / 1024
    
    # Contar linhas
    print(f"   Contando linhas...")
    count = count_csv_lines(filepath)
    
    # Range de datas (amostragem)
    print(f"   Analisando período (amostragem)...")
    date_min, date_max = get_csv_date_range(filepath)
    
    print(f"""
   Caminho:      {filepath}
   Tamanho:      {size_mb:.2f} MB
   Linhas:       {count:,}
   Período:      {date_min} a {date_max}
   Última mod:   {datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    return {
        'exists': True,
        'count': count,
        'size_mb': size_mb,
        'date_range': (date_min, date_max)
    }

def analyze_database(db_name, name):
    """Analisa um banco de dados SQLite"""
    print(f"\n{'='*80}")
    print(f"🗄️  {name}")
    print(f"{'='*80}")
    
    db_path = BASE_DIR / db_name
    
    if not db_path.exists():
        print(f"   ❌ Banco não encontrado: {db_path}")
        return {
            'exists': False,
            'count': 0,
            'size_mb': 0,
            'date_range': (None, None)
        }
    
    # Tamanho
    size_mb = db_path.stat().st_size / 1024 / 1024
    
    # Configurar Django para usar este banco
    original_db = os.environ.get('SQLITE_DB_NAME')
    os.environ['SQLITE_DB_NAME'] = db_name
    
    # Reconectar
    from django.db import connections
    connections.close_all()
    
    try:
        # Contar viagens
        count = Trip.objects.count()
        
        # Range de datas
        if count > 0:
            first_trip = Trip.objects.order_by('start_time').first()
            last_trip = Trip.objects.order_by('-start_time').first()
            date_min = first_trip.start_time.strftime('%Y-%m') if first_trip else None
            date_max = last_trip.start_time.strftime('%Y-%m') if last_trip else None
        else:
            date_min, date_max = None, None
        
        print(f"""
   Caminho:      {db_path}
   Tamanho:      {size_mb:.2f} MB
   Viagens:      {count:,}
   Período:      {date_min} a {date_max}
   Última mod:   {datetime.fromtimestamp(db_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
""")
        
        result = {
            'exists': True,
            'count': count,
            'size_mb': size_mb,
            'date_range': (date_min, date_max)
        }
        
    except Exception as e:
        print(f"   ❌ Erro ao analisar banco: {e}")
        result = {
            'exists': True,
            'count': 0,
            'size_mb': size_mb,
            'date_range': (None, None)
        }
    
    finally:
        # Restaurar banco original
        if original_db:
            os.environ['SQLITE_DB_NAME'] = original_db
        connections.close_all()
    
    return result

def main():
    print("\n" + "="*80)
    print("🔍 VERIFICAÇÃO DO DATASET COMPLETO")
    print("="*80)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Analisar CSVs
    csv_atual = analyze_csv(
        BASE_DIR / "dataRaw" / "consolidated_tembici_data.csv",
        "CSV ATUAL (Parcial - 2020-2022)"
    )
    
    csv_completo = analyze_csv(
        BASE_DIR / "dataRaw" / "consolidated_tembici_data_COMPLETO.csv",
        "CSV COMPLETO (2018-2023)"
    )
    
    # Analisar bancos
    db_atual = analyze_database(
        "db.sqlite3",
        "BANCO ATUAL (Parcial)"
    )
    
    db_completo = analyze_database(
        "db_COMPLETO.sqlite3",
        "BANCO COMPLETO"
    )
    
    # Comparação
    print(f"\n{'='*80}")
    print("📊 COMPARAÇÃO")
    print(f"{'='*80}")
    
    print("\n┌─────────────────────────────┬──────────────────┬──────────────────┐")
    print("│ Arquivo/Banco               │ Atual (Parcial)  │ Completo (Novo)  │")
    print("├─────────────────────────────┼──────────────────┼──────────────────┤")
    
    # CSVs
    print(f"│ CSV - Registros             │ {csv_atual['count']:>15,} │ {csv_completo['count']:>15,} │")
    print(f"│ CSV - Tamanho (MB)          │ {csv_atual['size_mb']:>15.2f} │ {csv_completo['size_mb']:>15.2f} │")
    if csv_atual['date_range'][0]:
        print(f"│ CSV - Período               │ {csv_atual['date_range'][0]:>6} a {csv_atual['date_range'][1]:<6} │", end="")
    else:
        print(f"│ CSV - Período               │ {'N/A':>16} │", end="")
    if csv_completo['date_range'][0]:
        print(f" {csv_completo['date_range'][0]:>6} a {csv_completo['date_range'][1]:<6} │")
    else:
        print(f" {'N/A':>16} │")
    
    print("├─────────────────────────────┼──────────────────┼──────────────────┤")
    
    # Bancos
    print(f"│ SQLite - Registros          │ {db_atual['count']:>15,} │ {db_completo['count']:>15,} │")
    print(f"│ SQLite - Tamanho (MB)       │ {db_atual['size_mb']:>15.2f} │ {db_completo['size_mb']:>15.2f} │")
    if db_atual['date_range'][0]:
        print(f"│ SQLite - Período            │ {db_atual['date_range'][0]:>6} a {db_atual['date_range'][1]:<6} │", end="")
    else:
        print(f"│ SQLite - Período            │ {'N/A':>16} │", end="")
    if db_completo['date_range'][0]:
        print(f" {db_completo['date_range'][0]:>6} a {db_completo['date_range'][1]:<6} │")
    else:
        print(f" {'N/A':>16} │")
    
    print("└─────────────────────────────┴──────────────────┴──────────────────┘")
    
    # Ganhos
    if csv_completo['exists'] and csv_atual['exists']:
        csv_gain = csv_completo['count'] - csv_atual['count']
        csv_gain_pct = (csv_gain / csv_atual['count'] * 100) if csv_atual['count'] > 0 else 0
        
        print(f"\n📈 GANHO NO CSV COMPLETO:")
        print(f"   + {csv_gain:,} registros ({csv_gain_pct:+.1f}%)")
    
    if db_completo['exists'] and db_atual['exists']:
        db_gain = db_completo['count'] - db_atual['count']
        db_gain_pct = (db_gain / db_atual['count'] * 100) if db_atual['count'] > 0 else 0
        
        print(f"\n📈 GANHO NO BANCO COMPLETO:")
        print(f"   + {db_gain:,} viagens ({db_gain_pct:+.1f}%)")
    
    # Status
    print(f"\n{'='*80}")
    print("✅ STATUS")
    print(f"{'='*80}")
    
    if csv_completo['exists']:
        print("✓ CSV completo gerado com sucesso")
    else:
        print("⚠ CSV completo ainda não foi gerado")
        print("  Execute: python scripts/consolidate_tembici_COMPLETO.py")
    
    if db_completo['exists'] and db_completo['count'] > 0:
        print("✓ Banco completo importado com sucesso")
        
        # Verificar taxa de importação
        if csv_completo['exists'] and csv_completo['count'] > 0:
            import_rate = db_completo['count'] / csv_completo['count'] * 100
            if import_rate >= 95:
                print(f"✓ Taxa de importação: {import_rate:.1f}% (EXCELENTE)")
            elif import_rate >= 80:
                print(f"⚠ Taxa de importação: {import_rate:.1f}% (ACEITÁVEL)")
            else:
                print(f"❌ Taxa de importação: {import_rate:.1f}% (BAIXA - reprocessar)")
    else:
        print("⚠ Banco completo ainda não foi importado")
        print("  Execute: python scripts/import_to_sqlite_COMPLETO.py")
    
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
