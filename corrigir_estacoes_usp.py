#!/usr/bin/env python3
"""
Script para corrigir os nomes das estações da USP no banco de dados
Baseado na lista oficial fornecida em 16/11/2025
"""

import sqlite3
import sys

print("=" * 80)
print("CORREÇÃO DOS NOMES DAS ESTAÇÕES DA USP")
print("=" * 80)
print()

# Correções a serem aplicadas (ID: novo_nome)
CORRECTIONS = {
    245: '245 - P1',
    246: '246 - Portão CPTM',
    251: '251 - FAU',
    253: '253 - Pedalusp Biênio',
    259: '259 - Vila Indiana',
    260: '260 - P3'
}

def show_current_state(conn):
    """Mostra o estado atual das estações"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT station_id, name 
        FROM ciclovias_station 
        WHERE station_id IN (245, 246, 251, 253, 259, 260)
        ORDER BY station_id
    """)
    
    print("ESTADO ATUAL DAS ESTAÇÕES A CORRIGIR:")
    print("-" * 80)
    for station_id, name in cursor.fetchall():
        print(f"  ID {station_id:3}: {name}")
    print()

def apply_corrections(conn, dry_run=True):
    """Aplica as correções"""
    cursor = conn.cursor()
    
    mode = "DRY-RUN (simulação)" if dry_run else "APLICANDO ALTERAÇÕES"
    print(f"MODO: {mode}")
    print("-" * 80)
    
    for station_id, new_name in sorted(CORRECTIONS.items()):
        # Buscar nome atual
        cursor.execute("SELECT name FROM ciclovias_station WHERE station_id = ?", (station_id,))
        result = cursor.fetchone()
        
        if result:
            old_name = result[0]
            print(f"\nID {station_id}:")
            print(f"  Antigo: {old_name}")
            print(f"  Novo:   {new_name}")
            
            if not dry_run:
                cursor.execute(
                    "UPDATE ciclovias_station SET name = ? WHERE station_id = ?",
                    (new_name, station_id)
                )
                print(f"  ✅ Atualizado!")
            else:
                print(f"  ℹ️  Seria atualizado (dry-run)")
        else:
            print(f"\n❌ ID {station_id} não encontrado no banco!")
    
    print()

def main():
    """Função principal"""
    
    # Conectar ao banco
    try:
        conn = sqlite3.connect('db.sqlite3')
        print("✅ Conectado ao banco de dados: db.sqlite3")
        print()
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        sys.exit(1)
    
    try:
        # Mostrar estado atual
        print("1. ESTADO ATUAL")
        print("=" * 80)
        show_current_state(conn)
        
        # Simulação
        print("\n2. SIMULAÇÃO DAS CORREÇÕES")
        print("=" * 80)
        apply_corrections(conn, dry_run=True)
        
        # Confirmar
        print("=" * 80)
        response = input("\nDeseja aplicar as correções no banco? (s/N): ").strip().lower()
        
        if response in ['s', 'sim', 'yes', 'y']:
            print("\n3. APLICANDO CORREÇÕES")
            print("=" * 80)
            apply_corrections(conn, dry_run=False)
            conn.commit()
            
            print("\n4. VERIFICANDO RESULTADO")
            print("=" * 80)
            show_current_state(conn)
            
            print("=" * 80)
            print("✅ CORREÇÕES APLICADAS COM SUCESSO!")
            print("=" * 80)
        else:
            print("\n❌ Operação cancelada. Nenhuma alteração foi feita.")
    
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        conn.close()

if __name__ == '__main__':
    main()
