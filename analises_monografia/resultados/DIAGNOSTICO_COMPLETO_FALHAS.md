# 🔍 DIAGNÓSTICO COMPLETO: Onde Cada Etapa Falhou

**Data:** 10/11/2025 23:10

---

## 📋 RESUMO EXECUTIVO

### Fluxo de Dados (3 etapas):
```
┌─────────────┐      ┌──────────────────────┐      ┌──────────┐
│   7 ZIPs    │ ──❌─→│ consolidated CSV      │ ──❌─→│  SQLite  │
│             │      │                      │      │          │
│ 2018-2023   │      │ 2020-2022 apenas     │      │ 40% CSV  │
└─────────────┘      └──────────────────────┘      └──────────┘
```

### Problemas Identificados:
1. ❌ **ETAPA 1:** ZIPs → CSV = **FALHOU** (dados 2018-2019 e 2023 não incluídos)
2. ❌ **ETAPA 2:** CSV → SQLite = **FALHOU** (só 40% foi importado)

---

## 📊 ETAPA 1: ZIPs → consolidated_tembici_data.csv

### Status: ❌ **INCOMPLETA**

### O Que Deveria Ter:
```
Período completo: 2018 a 2023 (5+ anos)
Estimativa: 20-25 milhões de viagens
```

### O Que TEM:
```
Período: 2020-01-01 a 2022-04-30 (2.3 anos)
Registros: 11,603,421
Tamanho: 1.84 GB
```

### O Que FALTA:
```
2018 (completo):  ~12 meses - formato XLSX ❌ NÃO PROCESSADO
2019 (completo):  ~12 meses - formato XLSX ❌ NÃO PROCESSADO
2022 (parcial):   Mai-Dez (8 meses) ⚠️ FALTAM
2023 (completo):  ~7 meses disponíveis ❌ NÃO PROCESSADO
```

### Por Que Falhou:
O script `consolidate_tembici_data.py` provavelmente:
- ✅ Processou CSVs de 2020-2021
- ✅ Processou parte de 2022 (Jan-Abr)
- ❌ NÃO processou arquivos XLSX de 2018-2019
- ❌ NÃO processou CSVs de 2023
- ❌ NÃO processou resto de 2022

**Possíveis causas:**
1. Script foi interrompido antes de terminar
2. Script só processa CSVs (ignora XLSXs)
3. Filtros de data aplicados
4. Erro não registrado no log

---

## 📊 ETAPA 2: consolidated_tembici_data.csv → db.sqlite3

### Status: ❌ **MUITO INCOMPLETA**

### O Que Deveria Ter:
```
CSV Total: 11,603,421 registros
Período: 2020-01-01 a 2022-04-30
```

### O Que TEM:
```
SQLite: 4,704,485 registros (40.6% do CSV!)
Período: 2020-01-01 a 2022-04-30 (mesmo período, mas menos dados)
```

### Distribuição no SQLite:

| Ano  | Mês | Viagens no SQLite |
|------|-----|-------------------|
| 2020 | Jan | 293,099 |
| 2020 | Fev | 253,415 |
| 2020 | Mar | 254,555 |
| 2020 | Abr | 171,013 |
| 2020 | Mai | 165,918 |
| 2020 | Jun | 149,364 |
| 2020 | Jul | 172,190 |
| 2020 | Ago | 185,596 |
| 2020 | Set | 211,317 |
| 2020 | Out | 207,622 |
| 2020 | Nov | 160,526 |
| 2020 | Dez | 130,352 |
| **2020 Total** | | **2,355,067** |
| | | |
| 2021 | Jan | 131,986 |
| 2021 | Fev | 118,317 |
| 2021 | Mar | 132,506 |
| 2021 | Abr | 140,598 |
| 2021 | Mai | 137,690 |
| 2021 | Jun | 136,317 |
| 2021 | Jul | 149,841 |
| 2021 | Ago | 158,638 |
| 2021 | Set | 175,209 |
| 2021 | Out | 140,975 |
| 2021 | Nov | 167,706 |
| 2021 | Dez | 133,710 |
| **2021 Total** | | **1,823,493** |
| | | |
| 2022 | Jan | 129,362 |
| 2022 | Fev | 149,123 |
| 2022 | Mar | 170,018 |
| 2022 | Abr | 177,522 |
| **2022 Total** | | **626,025** |
| | | |
| **TOTAL GERAL** | | **4,704,485** |

### O Que FALTA:
```
CSV Total:        11,603,421 registros
SQLite Importado:  4,704,485 registros (40.6%)
───────────────────────────────────────
FALTANDO:          6,898,936 registros (59.4%)
```

### Por Que Falhou:
**Hipóteses mais prováveis:**

1. **Import interrompido manualmente**
   - Você pode ter parado o processo com Ctrl+C
   - Processo foi morto por falta de memória
   - Sistema reiniciou durante import

2. **Filtros aplicados**
   - Comando usado: `--station-id-min` ou `--station-id-max`
   - Filtragem por estações específicas
   - Limite de registros: `--limit` ou `--max-trips`

3. **Erros de parsing**
   - Registros inválidos foram pulados
   - Erros em datas/coordenadas
   - Dados corrompidos

4. **Batch incompleto**
   - Último batch não foi commitado
   - Transação rollback por erro

### Como Verificar:
```bash
# Verifica logs de importação anteriores
grep -r "import" ~/tcc/ 2>/dev/null | grep -i "trip"

# Verifica histórico de comandos
history | grep "import_trips"
```

---

## 📈 GRÁFICO VISUAL DA SITUAÇÃO

```
DADOS DISPONÍVEIS vs PROCESSADOS

2018 ▓▓▓▓▓▓▓▓▓▓▓▓ (12 meses disponíveis em XLSX)
     ░░░░░░░░░░░░ (0 no CSV, 0 no SQLite) ❌

2019 ▓▓▓▓▓▓▓▓▓▓▓▓ (12 meses disponíveis em XLSX)
     ░░░░░░░░░░░░ (0 no CSV, 0 no SQLite) ❌

2020 ▓▓▓▓▓▓▓▓▓▓▓▓ (12 meses disponíveis em CSV)
     ████████████ (12 no CSV)
     █████░░░░░░░ (12 no SQLite, mas ~50% dos registros) ⚠️

2021 ▓▓▓▓▓▓▓▓▓▓▓▓ (12 meses disponíveis em CSV)
     ████████████ (12 no CSV)
     █████░░░░░░░ (12 no SQLite, mas ~50% dos registros) ⚠️

2022 ▓▓▓▓▓▓▓▓▓▓▓▓ (12 meses disponíveis em CSV)
     ████░░░░░░░░ (4 no CSV: Jan-Abr) ⚠️
     ████░░░░░░░░ (4 no SQLite: Jan-Abr) ⚠️

2023 ▓▓▓▓▓▓▓░░░░░ (7 meses disponíveis em CSV)
     ░░░░░░░░░░░░ (0 no CSV, 0 no SQLite) ❌

Legenda:
▓ = Dados existem nos ZIPs
█ = Dados processados
░ = Dados faltando
```

---

## ✅ PRÓXIMOS PASSOS PARA OPÇÃO C (Dataset Completo 2018-2023)

### PASSO 1: Backup de Tudo ⚠️ CRÍTICO
```bash
cd /home/gbiel/gabriel/usp/tcc/bikeProject-backEnd

# Backup do banco atual
cp db.sqlite3 db.sqlite3.BACKUP_ANTES_OPCAO_C_$(date +%Y%m%d_%H%M%S)

# Backup do CSV atual
cp dataRaw/consolidated_tembici_data.csv \
   dataRaw/consolidated_tembici_data.csv.BACKUP_2020-2022
```

### PASSO 2: Criar Novo Script de Consolidação
Precisamos criar um script que:
1. ✅ Processe CSVs de 2020-2022 (já funciona)
2. ✅ Processe XLSXs de 2018-2019 (NOVO!)
3. ✅ Processe CSVs de 2023 (NOVO!)
4. ✅ Gere `consolidated_tembici_data_COMPLETO_2018-2023.csv`

### PASSO 3: Re-importar para SQLite
```bash
# Limpar banco (ou criar novo)
python manage.py flush --no-input

# Importar dataset completo
python manage.py import_trips \
  dataRaw/consolidated_tembici_data_COMPLETO_2018-2023.csv \
  --batch-size 10000
```

### PASSO 4: Re-gerar Estatísticas
```bash
# Rodar script de estatísticas com dados completos
python analises_monografia/GERAR_ESTATISTICAS_COMPLETAS.py
```

### PASSO 5: Atualizar Monografia
- Atualizar período: 2018-2023 (5+ anos)
- Atualizar número de viagens: ~20-25M
- Re-gerar gráficos e tabelas

---

## 🎯 RESUMO FINAL

### Problema 1: ZIPs → CSV
- **Causa:** Script de consolidação não processou tudo
- **Impacto:** Faltam 2018, 2019, parte de 2022, e 2023
- **Solução:** Criar script melhorado que processe XLSXs e todos os CSVs

### Problema 2: CSV → SQLite
- **Causa:** Import incompleto (provavelmente interrompido ou com filtros)
- **Impacto:** Só 40% do CSV foi importado
- **Solução:** Re-importar CSV completo (ou novo CSV completo)

### Estimativas para Opção C:
- **Tempo total:** 12-48 horas
  - Criar script: 2-4h
  - Consolidar CSV: 4-12h (processar XLSXs é lento)
  - Importar SQLite: 6-24h (20-25M registros)
  - Regenerar análises: 2-4h
  
- **Tamanho final:**
  - CSV completo: ~3-5 GB
  - SQLite: ~8-12 GB
  - Total de viagens: ~20-25 milhões

---

**PRÓXIMA AÇÃO:** Você quer que eu crie o script de consolidação completo agora?
