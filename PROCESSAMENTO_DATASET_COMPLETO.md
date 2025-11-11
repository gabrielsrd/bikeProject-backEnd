# 🚴 Dataset COMPLETO - Instruções de Processamento

## 📋 Visão Geral

Este conjunto de scripts processa **TODOS** os dados disponíveis do Bike Sampa (2018-2023):

- **2018-2019**: Arquivos XLSX (formato antigo)
- **2020-2021**: CSVs (formato misto)  
- **2022**: CSVs Jan-Dez (formato novo)
- **2023**: CSVs até Jul (formato novo)

**Estimativa**: ~20-25 milhões de viagens

---

## 🎯 Diferença dos Scripts Atuais

### Scripts ATUAIS (parciais):
- ❌ `consolidate_tembici_data.py` → apenas ~50% dos dados (2020-2022 Jan-Abr)
- ❌ Banco `db.sqlite3` → apenas 4.7M viagens (40% do CSV)

### Scripts NOVOS (completos):
- ✅ `consolidate_tembici_COMPLETO.py` → 100% dos dados (2018-2023)
- ✅ `import_to_sqlite_COMPLETO.py` → importa 100% para `db_COMPLETO.sqlite3`
- ✅ `verificar_dataset_COMPLETO.py` → compara atual vs completo

---

## 🚀 Passo a Passo

### ETAPA 1: Consolidar ZIPs → CSV Completo

```bash
cd /home/gbiel/gabriel/usp/tcc/bikeProject-backEnd

# Executar consolidação COMPLETA
python3 scripts/consolidate_tembici_COMPLETO.py
```

**O que faz:**
1. Extrai TODOS os ZIPs em `dataRaw/Tembici-SaoPaulo/`
2. Processa XLSXs de 2018-2019 (formato antigo)
3. Processa CSVs de 2020-2023 (formatos variados)
4. Normaliza tudo para o formato padrão
5. Gera: `dataRaw/consolidated_tembici_data_COMPLETO.csv`

**Tempo estimado:** 30-60 minutos  
**Saída esperada:** ~3-5 GB, 20-25M viagens

**Logs:** `consolidacao_completa.log`

---

### ETAPA 2: Importar CSV → SQLite Completo

```bash
# Executar importação COMPLETA
python3 scripts/import_to_sqlite_COMPLETO.py
```

**O que faz:**
1. Lê `consolidated_tembici_data_COMPLETO.csv`
2. Importa TODAS as viagens para `db_COMPLETO.sqlite3`
3. Verifica progresso em tempo real
4. Permite recuperação se interrompido

**Tempo estimado:** 60-120 minutos  
**Saída esperada:** ~8-12 GB, 20-25M viagens

**Logs:** `importacao_completa.log`

**Opções interativas:**
- Continuar importação anterior (se interrompida)
- Limpar e recomeçar
- Cancelar

---

### ETAPA 3: Verificar Resultados

```bash
# Comparar datasets atual vs completo
python3 scripts/verificar_dataset_COMPLETO.py
```

**O que faz:**
- Compara `consolidated_tembici_data.csv` vs `consolidated_tembici_data_COMPLETO.csv`
- Compara `db.sqlite3` vs `db_COMPLETO.sqlite3`
- Mostra períodos cobertos
- Calcula ganhos

**Saída exemplo:**
```
┌─────────────────────────────┬──────────────────┬──────────────────┐
│ Arquivo/Banco               │ Atual (Parcial)  │ Completo (Novo)  │
├─────────────────────────────┼──────────────────┼──────────────────┤
│ CSV - Registros             │      11,603,421  │      23,456,789  │
│ SQLite - Registros          │       4,704,485  │      23,123,456  │
│ CSV - Período               │ 2020-01 a 2022-04│ 2018-01 a 2023-07│
│ SQLite - Período            │ 2020-01 a 2022-04│ 2018-01 a 2023-07│
└─────────────────────────────┴──────────────────┴──────────────────┘

📈 GANHO NO CSV COMPLETO:
   + 11,853,368 registros (+102.2%)

📈 GANHO NO BANCO COMPLETO:
   + 18,418,971 viagens (+391.4%)
```

---

## 📊 Estrutura de Arquivos

### ANTES (Parcial):
```
dataRaw/
  ├── consolidated_tembici_data.csv       (1.84 GB, 11.6M, 2020-2022)
  └── Tembici-SaoPaulo/
      └── [7 ZIPs não totalmente processados]

db.sqlite3                                (2.5 GB, 4.7M viagens)
```

### DEPOIS (Completo):
```
dataRaw/
  ├── consolidated_tembici_data.csv            (1.84 GB, 11.6M, 2020-2022) ← mantido
  ├── consolidated_tembici_data_COMPLETO.csv   (3-5 GB, 20-25M, 2018-2023) ← NOVO
  └── Tembici-SaoPaulo/
      └── [7 ZIPs totalmente processados]

db.sqlite3                                     (2.5 GB, 4.7M viagens) ← mantido
db_COMPLETO.sqlite3                            (8-12 GB, 20-25M viagens) ← NOVO
```

**✅ Seus dados atuais são preservados!**

---

## ⚙️ Requisitos

```bash
# Instalar dependências se necessário
pip install pandas openpyxl django tqdm
```

---

## 🐛 Resolução de Problemas

### Problema: "Erro ao processar XLSX"
**Solução:** Instalar `openpyxl`
```bash
pip install openpyxl
```

### Problema: "Memória insuficiente"
**Solução:** O script usa streaming (chunks), mas se ainda falhar:
```bash
# Editar consolidate_tembici_COMPLETO.py
# Linha ~350: reduzir chunk_rows de 200000 para 50000
```

### Problema: "Importação parou em 50%"
**Solução:** O script salva progresso. Execute novamente e escolha [1] Continuar

### Problema: "CSV corrompido"
**Solução:** 
```bash
# Deletar CSV incompleto e reprocessar
rm dataRaw/consolidated_tembici_data_COMPLETO.csv
python3 scripts/consolidate_tembici_COMPLETO.py
```

---

## 📝 Notas Importantes

### Formato do CSV

O formato segue **EXATAMENTE** o formato do `consolidated_tembici_data.csv` atual:

```csv
trip_id,duration_seconds,initial_station_name,start_time,final_station_name,end_time,birth_year,initial_station_latitude,initial_station_longitude,final_station_latitude,final_station_longitude
```

### Compatibilidade

- ✅ Todos os scripts existentes funcionam com ambos os CSVs
- ✅ Django models não precisam de alteração
- ✅ APIs e queries existentes funcionam
- ✅ Análises podem usar qualquer dos bancos

### Usar Banco Completo no Django

Para usar `db_COMPLETO.sqlite3` como banco padrão:

```bash
# Opção 1: Renomear (backup do antigo primeiro!)
cp db.sqlite3 db_parcial_backup.sqlite3
mv db_COMPLETO.sqlite3 db.sqlite3

# Opção 2: Editar myproject/settings.py
# Mudar 'NAME': BASE_DIR / 'db.sqlite3'
# Para:  'NAME': BASE_DIR / 'db_COMPLETO.sqlite3'
```

---

## 📈 Próximos Passos Após Importação

1. **Verificar cobertura temporal:**
   ```bash
   python3 scripts/verificar_dataset_COMPLETO.py
   ```

2. **Atualizar análises da monografia:**
   ```bash
   cd analises_monografia
   ./executar_todas_analises.sh
   ```

3. **Gerar estatísticas atualizadas:**
   ```bash
   python3 analises_monografia/GERAR_ESTATISTICAS_COMPLETAS.py
   ```

---

## ⏱️ Tempo Total Estimado

- **ETAPA 1** (Consolidação): 30-60 min
- **ETAPA 2** (Importação): 60-120 min  
- **ETAPA 3** (Verificação): < 5 min

**TOTAL: ~2-3 horas**

---

## 📞 Suporte

Logs detalhados são salvos em:
- `consolidacao_completa.log` (ETAPA 1)
- `importacao_completa.log` (ETAPA 2)

Em caso de erro, verifique os logs para detalhes.

---

## ✅ Checklist

- [ ] Executar `consolidate_tembici_COMPLETO.py`
- [ ] Verificar que CSV completo foi gerado (~3-5 GB)
- [ ] Executar `import_to_sqlite_COMPLETO.py`  
- [ ] Verificar que banco completo foi criado (~8-12 GB)
- [ ] Executar `verificar_dataset_COMPLETO.py`
- [ ] Confirmar taxa de importação ≥ 95%
- [ ] Atualizar análises da monografia

---

**Última atualização:** 2025-11-10  
**Versão:** 2.0 - Dataset Completo
