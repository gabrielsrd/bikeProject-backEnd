# 📊 Resumo Executivo: Situação dos Dados Tembici

**Data da Análise:** 10 de novembro de 2025  
**Responsável:** Script VERIFICAR_DADOS_DISPONIVEIS.py

---

## 🎯 Situação Atual

### Arquivo Consolidado Existente
- **Arquivo:** `consolidated_tembici_data.csv`
- **Tamanho:** 1.84 GB
- **Registros:** 11,603,422
- **Período:** 2020-01-01 a 2022-04-30 (2 anos e 4 meses)
- **Última modificação:** 02/11/2025 14:40

### Banco de Dados SQLite
- **Arquivo:** `db.sqlite3`
- **Tamanho:** 1.7 GB
- **Registros importados:** 4,704,485 (40.6% do CSV)
- **Período no DB:** 2020-01-01 a 2022-04-30

---

## ⚠️ PROBLEMA IDENTIFICADO

### 1. CSV Incompleto (2020-2022 apenas)
O arquivo `consolidated_tembici_data.csv` **NÃO inclui** todos os dados disponíveis:

✅ **Incluído:**
- 2020: Janeiro a Dezembro (completo)
- 2021: Janeiro a Dezembro (completo)
- 2022: Janeiro a Abril (parcial)

❌ **NÃO Incluído:**
- **2018:** ~12 meses (formato XLSX)
- **2019:** ~12 meses (formato XLSX)
- **2022:** Maio a Dezembro (faltam 8 meses!)
- **2023:** Janeiro a Julho (formato CSV disponível)

### 2. Banco de Dados Incompleto
O SQLite só tem **4.7M** dos **11.6M** registros do CSV (40.6%)

Possíveis causas:
- Import interrompido
- Filtros aplicados durante import
- Erros de importação não registrados

---

## 📦 Dados Disponíveis nos ZIPs

### ZIPs Analisados (7 arquivos)

| ZIP | Conteúdo | Período | Status |
|-----|----------|---------|--------|
| `TemBici-São Paulo-20190516` | 16 XLSXs | 2018-2019 | ❌ NÃO processado |
| `drive-download-20200210` | 16 XLSXs | 2019 | ❌ NÃO processado |
| `BikeSampa-20210216` | 7 CSVs + 27 XLSXs | 2018-2020 | ✅ Parcialmente (só 2020) |
| `BikeSampa-20220801` | 30 CSVs + 28 XLSXs | 2018-2022 | ✅ Parcialmente |
| `Bike Sampa 2022-2023` | 12 CSVs | 2022 | ⚠️ Parcialmente? |
| `São Paulo-20230823-001` | 38 CSVs + 11 XLSXs | 2021-2023 | ❌ NÃO processado |
| `São Paulo-20230823-002` | 23 CSVs + 17 XLSXs | 2020-2023 | ❌ NÃO processado |

### Estimativa de Registros por Ano

Baseado na amostra de CSVs analisados:

| Ano | Registros (amostra) | Status | Formato |
|-----|---------------------|--------|---------|
| **2018** | Desconhecido | ❌ NÃO incluído | XLSX |
| **2019** | Desconhecido | ❌ NÃO incluído | XLSX |
| **2020** | ~1,937,000 | ✅ Incluído | CSV |
| **2021** | ~1,705,000 | ✅ Incluído | CSV |
| **2022** | ~1,252,000 | ⚠️ Parcial (Jan-Abr) | CSV |
| **2023** | Desconhecido | ❌ NÃO incluído | CSV |

---

## 💡 Análise e Recomendações

### Cenário 1: Usar Apenas Dados Atuais (2020-2022)
**Prós:**
- ✅ Dados já consolidados e testados
- ✅ Período suficiente para análise (2.3 anos)
- ✅ ~11.6 milhões de viagens
- ✅ Não requer reprocessamento

**Contras:**
- ❌ Perde 2 anos de dados (2018-2019)
- ❌ Perde dados de 2023
- ❌ Monografia terá período limitado

**Recomendação:** ✅ **RECOMENDADO** se você quer publicar rápido

### Cenário 2: Processar Todos os Dados (2018-2023)
**Prós:**
- ✅ Dataset completo de 5+ anos
- ✅ Mais robusto para conclusões
- ✅ Inclui período pós-pandemia (2023)
- ✅ Análise temporal mais rica

**Contras:**
- ❌ Precisa processar arquivos XLSX de 2018-2019
- ❌ Tempo adicional de processamento (~4-12 horas)
- ❌ Risco de erros no processamento
- ❌ Pode atrasar finalização da monografia

**Recomendação:** ⚠️ **CONSIDERAR** se você tem tempo

### Cenário 3: Híbrido - Adicionar Apenas 2023
**Prós:**
- ✅ Dados mais recentes (2023)
- ✅ Período pós-pandemia
- ✅ Relativamente rápido (já são CSVs)
- ✅ Melhora sem grande esforço

**Contras:**
- ❌ Ainda perde 2018-2019
- ❌ Requer reprocessamento

**Recomendação:** 🤔 **BOA OPÇÃO** se você quer melhorar sem grande risco

---

## 🔧 Plano de Ação Sugerido

### OPÇÃO A: Continuar com Dados Atuais (RÁPIDO)

```bash
# 1. Aceitar que o período é 2020-2022
# 2. Re-importar CSV completo para SQLite (resolver 40% vs 100%)

cd /home/gbiel/gabriel/usp/tcc/bikeProject-backEnd
source venv/bin/activate

# Backup do DB atual
cp db.sqlite3 db.sqlite3.backup_20251110

# Re-importar tudo
python manage.py flush --no-input  # Limpa DB
python manage.py migrate
python manage.py import_trips dataRaw/consolidated_tembici_data.csv

# 3. Atualizar monografia com período correto: 2020-2022
```

**Tempo estimado:** 2-4 horas  
**Risco:** Baixo

### OPÇÃO B: Processar Dados 2023 (MÉDIO ESFORÇO)

```bash
# 1. Criar novo consolidated incluindo 2023
cd /home/gbiel/gabriel/usp/tcc/bikeProject-backEnd
source venv/bin/activate

# 2. Executar script para adicionar 2023
python scripts/consolidate_tembici_data.py  # Ou criar novo script

# 3. Re-importar para SQLite
python manage.py flush --no-input
python manage.py migrate
python manage.py import_trips dataRaw/consolidated_tembici_data_2020-2023.csv

# 4. Atualizar monografia com período: 2020-2023
```

**Tempo estimado:** 6-12 horas  
**Risco:** Médio

### OPÇÃO C: Dataset Completo 2018-2023 (LONGO PRAZO)

```bash
# 1. Criar script para processar XLSXs de 2018-2019
# 2. Consolidar TUDO: 2018-2023
# 3. Re-importar
# 4. Re-gerar todas as análises

# Tempo estimado: 1-3 dias
# Risco: Alto
```

**Tempo estimado:** 1-3 dias  
**Risco:** Alto (possíveis erros no processamento de XLSX)

---

## 📋 Checklist de Decisão

Responda estas perguntas para decidir:

- [ ] **Prazo:** Quanto tempo você tem até a entrega?
  - < 1 semana: OPÇÃO A
  - 1-2 semanas: OPÇÃO B
  - > 2 semanas: OPÇÃO C

- [ ] **Qualidade:** A monografia precisa do dataset completo?
  - Não: OPÇÃO A
  - Preferivelmente: OPÇÃO B
  - Sim: OPÇÃO C

- [ ] **Risco:** Você pode arriscar problemas de processamento?
  - Não: OPÇÃO A
  - Sim, controlado: OPÇÃO B
  - Sim: OPÇÃO C

---

## 📞 Próximos Passos Imediatos

1. **DECIDIR** qual opção seguir (A, B ou C)

2. **BACKUPS:** Fazer backup de tudo antes de qualquer mudança
   ```bash
   cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d)
   cp dataRaw/consolidated_tembici_data.csv dataRaw/consolidated_tembici_data.csv.backup
   ```

3. **EXECUTAR:** Seguir o plano da opção escolhida

4. **VALIDAR:** Verificar que dados foram importados corretamente

5. **ATUALIZAR:** Regenerar estatísticas e atualizar monografia

---

## 📝 Arquivos de Referência

- `/analises_monografia/VERIFICAR_DADOS_DISPONIVEIS.py` - Script de análise
- `/analises_monografia/resultados/relatorio_dados_disponiveis_*.txt` - Relatório completo
- `/analises_monografia/resultados/RESUMO_SITUACAO_DADOS.md` - Este arquivo
- `/scripts/consolidate_tembici_data.py` - Script original de consolidação

---

**Última atualização:** 10/11/2025 23:00
