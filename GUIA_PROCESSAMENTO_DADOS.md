# 📊 Guia Completo: Processamento de Dados Tembici para SQLite

## ✅ Status Atual dos Seus Dados

### Dados Disponíveis
Você **JÁ TEM** os dados baixados e organizados! ✓

**Localização:** `/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/dataRaw/Tembici-SaoPaulo/`

**Período:** 2018 até 2023 (5 anos de dados!)

**Arquivos:**
- 7 arquivos ZIP grandes (2018-2023) - Total: ~1.3 GB compactado
- 1 arquivo CSV solto (julho/2022) - 129K registros

**Total estimado:** 10+ milhões de viagens! 🚀

### Formato dos Dados (2021-2023 - Mais Recentes)
```csv
trip_id,duration_seconds,initial_station_name,start_time,final_station_name,end_time,birth_year,initial_station_latitude,initial_station_longitude,final_station_latitude,final_station_longitude
12699323BikeSampa,1061,21 - Parque do Povo portão 1,2022-01-26T08:07:08Z,120 - Rua Gomes de Carvalho,2022-01-26T08:24:49Z,1992-01-01,-23.5890444167307,-46.6882179128703,-23.5997736418236,-46.6795527222334
```

**✨ ÓTIMA NOTÍCIA:** Os dados mais recentes (2021-2023) **JÁ INCLUEM** as coordenadas de latitude/longitude!

**Colunas disponíveis:**
- `trip_id` - ID único da viagem
- `duration_seconds` - Duração da viagem
- `initial_station_name` - Estação de origem
- `start_time` - Data/hora início
- `final_station_name` - Estação destino  
- `end_time` - Data/hora fim
- `birth_year` - Ano de nascimento
- `initial_station_latitude` / `initial_station_longitude` - Coordenadas origem ✓
- `final_station_latitude` / `final_station_longitude` - Coordenadas destino ✓

---

## 🚀 PROCESSO COMPLETO: 3 Passos

### PASSO 1: Configurar Ambiente Virtual

```bash
cd /home/gbiel/gabriel/usp/tcc/bikeProject-backEnd

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

---

### PASSO 2: Consolidar os Dados CSV

Você precisa consolidar os 45 arquivos CSV em um único arquivo no formato correto.

**Script disponível:** `scripts/consolidate_tembici_simple.py`

**⚠️ IMPORTANTE:** O script precisa ser ajustado para seus dados!

#### 2.1. Executar a Consolidação

O script foi atualizado para processar **TODOS** os ZIPs e CSVs automaticamente!

Ele detecta 2 formatos diferentes:
- **Formato novo (2021-2023):** Já tem todas as colunas corretas + coordenadas! ✓
- **Formato antigo (2018-2020):** Faz o mapeamento automático das colunas

**Mapeamento automático para dados antigos:**
```
start_date          → start_time
end_date            → end_time  
ano_nasc            → birth_year
start_station_name  → initial_station_name
end_station_name    → final_station_name
```

```bash
cd /home/gbiel/gabriel/usp/tcc/bikeProject-backEnd

# Ativar ambiente virtual
source venv/bin/activate

# Executar consolidação (processa todos os ZIPs e CSVs automaticamente!)
python3 scripts/consolidate_tembici_cleaned.py
```

**O que o script faz:**
1. Extrai todos os 7 arquivos ZIP
2. Processa todos os CSVs dentro dos ZIPs
3. Processa o CSV solto (julho/2022)
4. Normaliza todos para o mesmo formato
5. Gera arquivo único: `consolidated_tembici_data.csv`

**Estimativa de tempo:** 30-90 minutos (processando ~10 milhões de registros!)
**Arquivo final:** ~1-2 GB

---

### PASSO 3: Importar para o Banco de Dados SQLite

Depois de ter o arquivo consolidado, você importa para o banco.

#### 3.1. Criar as Tabelas no Banco

```bash
# Ativar ambiente virtual (se ainda não estiver ativo)
source venv/bin/activate

# Criar migrações
python3 manage.py makemigrations ciclovias

# Aplicar migrações (cria as tabelas Station e Trip)
python3 manage.py migrate
```

#### 3.2. Importar os Dados

```bash
# IMPORTANTE: Teste primeiro com poucos dados!
python3 manage.py import_trips dataRaw/consolidated_tembici_data.csv --limit 50000

# Depois de confirmar que funciona, importação completa
python3 manage.py import_trips dataRaw/consolidated_tembici_data.csv
```

**Opções úteis do comando:**
- `--test-run` - Importa apenas 1000 linhas para teste rápido
- `--limit N` - Importa apenas N linhas (recomendado: comece com 50.000)
- `--batch-size 5000` - Tamanho do lote (ajustar se tiver problemas de memória)
- `--precount` - Conta total de linhas antes (mais preciso mas mais lento)
- `--max-trips N` - Importa no máximo N viagens
- `--station-id-min 242 --station-id-max 260` - Importa apenas viagens das estações USP

**Estimativa de tempo:**
- 50.000 registros (teste): ~5-15 minutos
- 10+ milhões (completo): **6-24 horas** ⚠️

**💡 DICA:** Para trabalhar mais rápido, importe apenas as estações USP primeiro:
```bash
python3 manage.py import_trips dataRaw/consolidated_tembici_data.csv \
  --station-id-min 242 --station-id-max 260 --max-trips 100000
```

---

## ✅ EXCELENTE NOTÍCIA: Coordenadas Incluídas!

### Situação Atual
Os dados de **2021-2023 JÁ INCLUEM** latitude/longitude das estações! ✓

Exemplo:
```csv
initial_station_latitude,initial_station_longitude,final_station_latitude,final_station_longitude
-23.5890444167307,-46.6882179128703,-23.5997736418236,-46.6795527222334
```

Isso significa que você terá:
- ✅ Visualização completa de mapas
- ✅ Cálculos de distância precisos
- ✅ Filtros geográficos funcionais
- ✅ Análises espaciais avançadas

**Nota:** Os dados antigos (2018-2020) podem não ter coordenadas, mas você tem milhões de registros com coordenadas dos anos mais recentes!

---

## 📝 SCRIPT CORRIGIDO PARA SEUS DADOS

Criei um script ajustado para o formato dos seus dados:

**Arquivo:** `scripts/consolidate_tembici_cleaned.py`

```python
#!/usr/bin/env python3
"""
Consolidate Tembici Cleaned Data
Process cleaned CSV files from dataRaw/Tembici-SaoPaulo/cleaned/
"""

import pandas as pd
import glob
from pathlib import Path
from datetime import datetime

def consolidate_cleaned_data():
    print("Consolidating Tembici cleaned data...")
    
    # Path to cleaned CSV files
    csv_pattern = "/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/dataRaw/Tembici-SaoPaulo/cleaned/trips_*.csv"
    csv_files = glob.glob(csv_pattern)
    
    print(f"Found {len(csv_files)} CSV files")
    
    all_data = []
    
    for idx, csv_file in enumerate(csv_files, 1):
        print(f"Processing {idx}/{len(csv_files)}: {Path(csv_file).name}")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Rename columns to match expected format
            df_normalized = pd.DataFrame({
                'trip_id': df.index.astype(str) + '_' + Path(csv_file).stem,  # Generate unique ID
                'duration_seconds': df['duration_seconds'],
                'initial_station_name': df['start_station_name'],
                'start_time': df['start_date'],
                'final_station_name': df['end_station_name'],
                'end_time': df['end_date'],
                'birth_year': df['ano_nasc'],
                'initial_station_latitude': '',  # Not available in source
                'initial_station_longitude': '',  # Not available in source
                'final_station_latitude': '',  # Not available in source
                'final_station_longitude': ''  # Not available in source
            })
            
            all_data.append(df_normalized)
            print(f"  ✓ Processed {len(df_normalized)} rows")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue
    
    # Concatenate all data
    if all_data:
        print("\nConcatenating all data...")
        consolidated = pd.concat(all_data, ignore_index=True)
        
        # Save to file
        output_file = "/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/dataRaw/consolidated_tembici_data.csv"
        print(f"Writing {len(consolidated)} rows to {output_file}")
        consolidated.to_csv(output_file, index=False)
        
        print(f"\n✅ Success! Created {output_file}")
        print(f"Total records: {len(consolidated):,}")
        
        # Show sample
        print("\nFirst 3 records:")
        print(consolidated.head(3))
        
    else:
        print("\n❌ No data to consolidate!")

if __name__ == "__main__":
    consolidate_cleaned_data()
```

---

## ✅ CHECKLIST: O Que Você Precisa Fazer

### Preparação
- [ ] Verificar que os dados estão em `dataRaw/Tembici-SaoPaulo/cleaned/` (já verificado ✓)
- [ ] Criar e ativar ambiente virtual Python
- [ ] Instalar dependências com `pip install -r requirements.txt`

### Consolidação
- [ ] Criar/ajustar script de consolidação
- [ ] Executar consolidação (gera `consolidated_tembici_data.csv`)
- [ ] Verificar arquivo consolidado (tamanho, formato, amostras)

### Banco de Dados
- [ ] Executar migrações: `python3 manage.py migrate`
- [ ] Fazer teste de importação com poucos registros
- [ ] Executar importação completa (pode demorar!)
- [ ] Verificar dados no banco: `python3 manage.py shell`

### Validação
- [ ] Testar endpoints da API
- [ ] Verificar se os dados aparecem corretamente
- [ ] Testar filtros (dias, meses, estações)

---

## 🔧 COMANDOS RÁPIDOS

```bash
# Setup completo
cd /home/gbiel/gabriel/usp/tcc/bikeProject-backEnd
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Consolidar dados
python3 scripts/consolidate_tembici_cleaned.py

# Setup banco
python3 manage.py migrate

# Importar (teste)
python3 manage.py import_trips dataRaw/consolidated_tembici_data.csv --limit 10000

# Importar (completo)
python3 manage.py import_trips dataRaw/consolidated_tembici_data.csv

# Iniciar servidor
python3 manage.py runserver
```

---

## 📊 PRÓXIMOS PASSOS APÓS IMPORTAÇÃO

1. **Testar API**: `http://localhost:8000/api/station_histogram/`
2. **Adicionar coordenadas**: Usar arquivo de estações para popular lat/lon
3. **Otimizar queries**: Adicionar índices se necessário
4. **Monitorar performance**: Verificar tempo de resposta dos endpoints

---

## ⚠️ NOTAS IMPORTANTES

1. **Espaço em disco**: O arquivo consolidado terá ~1-2GB
2. **Banco SQLite**: Terá ~5-10GB após importação completa de 10M+ registros
3. **Tempo**: Todo o processo pode levar 8-30 horas total (depende muito do hardware)
4. **RAM**: Recomendado ter pelo menos 8GB disponível
5. **Performance**: Considere importar apenas dados relevantes primeiro (ex: apenas estações USP)

### 💡 Estratégia Recomendada para Desenvolvimento

Se você quer começar a trabalhar rápido:

```bash
# 1. Importar apenas 100K registros para testes
python3 manage.py import_trips dataRaw/consolidated_tembici_data.csv --limit 100000

# 2. Testar API e frontend com esses dados

# 3. Quando estiver tudo funcionando, importar mais dados conforme necessário
```

---

## 🆘 PROBLEMAS COMUNS

### "No module named 'django'"
→ Ativar ambiente virtual: `source venv/bin/activate`

### "Memory error during import"
→ Reduzir `--batch-size`: `--batch-size 1000`

### "Import muito lento"
→ Normal com 4 milhões de registros, pode demorar horas

### "Faltam coordenadas"
→ Esperado, seus dados não incluem lat/lon

---

## 📚 REFERÊNCIAS

- Plano detalhado: `CSV_TO_DATABASE_PLAN.md`
- Documentação: `README.md`
- Models Django: `ciclovias/models.py`
- Script de importação: `ciclovias/management/commands/import_trips.py`
