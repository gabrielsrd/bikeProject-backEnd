# 📊 ANÁLISES FOCADAS NO CAMPUS USP - RESULTADOS

**Data:** 13 de Novembro de 2025, 23:20h  
**Dataset:** 91.976 viagens do campus (origem OU destino nas 19 estações USP)  
**Viagens internas:** 61.082 (origem E destino no campus)

---

## 🎯 OBJETIVO

Refazer as análises da Seção 5.8 usando **exclusivamente** o dataset do campus USP, em vez do dataset completo de São Paulo (9+ milhões de viagens).

Isso garante que os insights reflitam os padrões reais do campus, não do sistema urbano como um todo.

---

## 📈 RESULTADOS PRINCIPAIS

### 1. HORÁRIOS ACADÊMICOS (Dataset Campus: 91.976 viagens)

**Pico Absoluto:** 17h com 8.215 viagens (8,9% do total)

**Viagens nos Horários Típicos de Aula USP:**
- **8h:**  4.138 viagens (4,50%)
- **10h:** 5.043 viagens (5,48%)
- **14h:** 5.306 viagens (5,77%)
- **16h:** 7.453 viagens (8,10%) ⭐ PICO
- **19h:** 5.325 viagens (5,79%)

**Verificação de Picos Pré-Aula:**
- 7h→8h: **-1.075 viagens** (QUEDA antes do início das aulas)
- 9h→10h: **+565 viagens** (AUMENTO antes da segunda aula)
- 13h→14h: **-953 viagens** (QUEDA após almoço)
- 15h→16h: **+1.620 viagens** (AUMENTO forte) ⭐
- 18h→19h: **-2.139 viagens** (QUEDA após pico de saída)

**💡 INSIGHTS:**
- ✅ Pico mais forte às 16h-17h (saída do campus)
- ✅ Aumento significativo 15h→16h sugere preparação para aulas das 16h
- ⚠️ QUEDA antes das 8h sugere que alunos chegam mais cedo (7h)
- ✅ Horários de aula (10h, 14h, 16h) têm picos claros

**Arquivo gerado:** `analise_11_campus_horarios_academicos.png`

---

### 2. DURAÇÃO DAS VIAGENS INTERNAS (61.082 viagens)

**Estatísticas de Duração:**
- **Média:** 198,5 minutos (3h 18min) ⚠️
- **Mediana:** 33,7 minutos
- **Q1 (25%):** 11,4 minutos
- **Q3 (75%):** 229,7 minutos
- **Mínimo:** 1,0 minuto
- **Máximo:** 111.013 minutos (77 dias!) 🤯

**Classificação por Duração:**
- **Curtas (< 10 min):** 12.890 viagens (21,1%) - ÚLTIMA MILHA
- **Médias (10-30 min):** 15.955 viagens (26,1%) - TRANSPORTE ENTRE UNIDADES
- **Longas (>= 30 min):** 32.237 viagens (52,8%) - LAZER/OUTROS ⚠️

**💡 INTERPRETAÇÃO:**
- ⚠️ **Mediana de 33,7 min** sugere uso predominante para transporte entre unidades
- ⚠️ **52,8% das viagens > 30 min** indica que muitas bicicletas ficam estacionadas por períodos longos
- ✅ **21,1% < 10 min** confirma uso de última milha, mas não é majoritário
- 🤯 **Duração máxima absurda** sugere problemas de devolução/sistema

**Conclusão:** Sistema é usado primariamente para **transporte entre unidades** (médio prazo), não última milha (curto prazo).

**Arquivo gerado:** `analise_11_campus_duracao_viagens.png`

---

### 3. PADRÃO DE "MARÉ" NOS PORTAIS

Análise de saldo líquido (Partidas - Chegadas) por hora nas 3 estações-portal:

#### 🚇 METRÔ BUTANTÃ (Principal Portal)
- **Total partidas:** 8.506
- **Total chegadas:** 10.679
- **Saldo total:** **-2.173** (mais gente SAINDO do campus)
- **Hora de maior entrada:** 7h (saldo: +453)
- **Hora de maior saída:** 17h (saldo: -522) ⭐

**💡 Padrão "maré" CLARO:**
- Manhã (7h-9h): Saldo POSITIVO (mais partidas = entrada no campus)
- Tarde (16h-18h): Saldo NEGATIVO (mais chegadas = saída do campus)

#### 🚂 PORTÃO CPTM
- **Total partidas:** 4.898
- **Total chegadas:** 4.774
- **Saldo total:** **+124** (equilibrado)
- **Hora de maior entrada:** 6h (saldo: +213)
- **Hora de maior saída:** 16h (saldo: -204)

**💡 Padrão "maré" moderado** (entrada mais cedo que Metrô)

#### 🚪 P1 (Portão 1)
- **Total partidas:** 4.375
- **Total chegadas:** 4.463
- **Saldo total:** **-88** (equilibrado)
- **Hora de maior entrada:** 7h (saldo: +272)
- **Hora de maior saída:** 18h (saldo: -137)

**💡 Padrão "maré" presente** mas menos acentuado

**Arquivo gerado:** `analise_11_campus_mare_portais.png`

---

### 4. ORIGENS PARA BANDEJÕES (Horário de Almoço 11h-14h)

#### 🍽️ BANDEJÃO CENTRAL (Principal)

**Top 15 Origens:**
1. **Próprio Bandejão Central:** 1.717 viagens (viagens circulares!)
2. Bandejão Química: 248 viagens
3. Portão CPTM: 186 viagens
4. Pedalusp Biênio: 183 viagens
5. P1: 176 viagens
6. FAU: 170 viagens
7. **Metrô Butantã:** 158 viagens ⭐
8. Praça Monte Castelo: 146 viagens
9. Biblioteca Brasiliana: 100 viagens
10. Bancos/Reitoria: 79 viagens
11. CEPE: 78 viagens
12. Vila Indiana: 73 viagens
13. Terminal de Ônibus USP: 60 viagens
14. Bandejão Física: 55 viagens
15. Odontologia: 49 viagens

**💡 INSIGHTS:**
- 🤔 **1.717 viagens circulares** (mesmo origem/destino) sugerem problema de dados OU pessoas que saem e voltam
- ✅ **Metrô Butantã como origem** confirma integração modal (alunos vêm de fora almoçar)
- ✅ Origens distribuídas pelo campus (FAU, Biênio, CEPE) mostram uso interno

**Arquivo gerado:** `analise_11_campus_bandejao_38476_origens.png`

#### 🍽️ BANDEJÃO QUÍMICA

**Top 3 Origens:**
1. Bandejão Central: 123 viagens
2. Vila Indiana: 65 viagens
3. P1: 54 viagens

**💡 INSIGHTS:**
- Uso mais concentrado em áreas próximas (Vila Indiana, P1)
- Menor demanda que Bandejão Central

**Arquivo gerado:** `analise_11_campus_bandejao_56642_origens.png`

#### 🍽️ BANDEJÃO PREFEITURA

**Top 3 Origens:**
1. Pedalusp Biênio: 46 viagens
2. Bandejão Central: 42 viagens
3. FAU: 18 viagens

**💡 INSIGHTS:**
- Menor demanda geral
- Uso concentrado em Biênio e FAU (proximidade geográfica)

**Arquivo gerado:** `analise_11_campus_bandejao_56713_origens.png`

---

## 🎓 COMPARAÇÃO: CAMPUS vs SÃO PAULO

### Análise Anterior (Errada - Dataset SP completo)

| Métrica | Valor (9,18M viagens SP) |
|---------|--------------------------|
| Viagens dias úteis | 7.149.516 (77,9%) |
| Razão semana/FDS | 3,5x |
| Pico horário | 18h com 857.008 viagens |

### Análise Correta (Dataset Campus)

| Métrica | Valor (91.976 viagens campus) |
|---------|-------------------------------|
| Viagens totais | 91.976 |
| Pico horário | 17h com 8.215 viagens (8,9%) |
| Pico acadêmico | 16h com 7.453 viagens (8,1%) |

**💡 DIFERENÇA CRÍTICA:**
- A análise anterior usava TODOS os dados de SP
- A análise correta usa APENAS viagens do campus
- **Os padrões são diferentes!** O campus tem pico mais cedo (16h-17h) que a cidade (18h)

---

## ✅ RESPOSTAS ÀS PERGUNTAS ORIGINAIS

### 1. "Refazer análises usando exclusivamente dataset de 92.737 viagens"
✅ **FEITO** - Usamos filtro `Q(initial_station_id__in=ESTACOES_USP) | Q(final_station_id__in=ESTACOES_USP)`

### 2. "Duração média das 63.598 viagens internas - última milha ou transporte entre unidades?"
✅ **RESPOSTA:** Mediana de 33,7 min sugere **TRANSPORTE ENTRE UNIDADES**, não última milha
- Apenas 21,1% < 10 min (última milha)
- 26,1% entre 10-30 min (transporte entre unidades)
- 52,8% > 30 min (lazer/outros/problemas de devolução)

### 3. "Gráfico de 24h mostrando saldo (Partidas - Chegadas) nos portais"
✅ **FEITO** - Arquivo: `analise_11_campus_mare_portais.png`
- Metrô Butantã: padrão "maré" CLARO (entrada 7h, saída 17h)
- Portão CPTM: padrão moderado (entrada 6h, saída 16h)
- P1: padrão presente (entrada 7h, saída 18h)

### 4. "Principais origens para bandejões (11h-14h)"
✅ **FEITO** - Top 15 para cada bandejão identificado
- Bandejão Central: 1.717 viagens circulares + Metrô Butantã (158)
- Bandejão Química: Vila Indiana (65) + P1 (54)
- Bandejão Prefeitura: Biênio (46) + FAU (18)

### 5. "Correlacionar picos com horários de aula (8h, 10h, 14h, 16h)"
✅ **FEITO** - Picos identificados:
- 16h é o MAIOR pico acadêmico (7.453 viagens, 8,1%)
- Aumento 15h→16h: +1.620 viagens (forte)
- 10h e 14h têm picos moderados (~5%)
- 8h tem QUEDA vs 7h (alunos chegam mais cedo)

---

## 📊 ARQUIVOS GERADOS

### Gráficos (6 PNG, 300 dpi)
1. `analise_11_campus_horarios_academicos.png` - Distribuição horária com horários de aula
2. `analise_11_campus_duracao_viagens.png` - Histograma + boxplot de durações
3. `analise_11_campus_mare_portais.png` - Saldo (Partidas - Chegadas) nos 3 portais
4. `analise_11_campus_bandejao_38476_origens.png` - Top 15 origens Bandejão Central
5. `analise_11_campus_bandejao_56642_origens.png` - Top 15 origens Bandejão Química
6. `analise_11_campus_bandejao_56713_origens.png` - Top 15 origens Bandejão Prefeitura

### Dados CSV (7 arquivos)
1. `analise_11_campus_horarios_dados.csv` - Viagens por hora
2. `analise_11_campus_duracao_stats.csv` - Estatísticas de duração
3. `analise_11_campus_mare_56861.csv` - Saldo Metrô Butantã por hora
4. `analise_11_campus_mare_38637.csv` - Saldo Portão CPTM por hora
5. `analise_11_campus_mare_48848.csv` - Saldo P1 por hora
6. `analise_11_campus_bandejao_38476_origens.csv` - Origens Bandejão Central
7. `analise_11_campus_bandejao_56642_origens.csv` - Origens Bandejão Química
8. `analise_11_campus_bandejao_56713_origens.csv` - Origens Bandejão Prefeitura

---

## 🔍 INSIGHTS CRÍTICOS PARA A MONOGRAFIA

### 1. Duração Mediana vs Média
- **Média:** 198,5 min (inflada por outliers extremos)
- **Mediana:** 33,7 min (valor mais representativo)
- **Use a MEDIANA** na monografia!

### 2. Padrão "Maré" Confirmado
- Metrô Butantã: entrada 7h (+453), saída 17h (-522)
- Padrão clássico casa→universidade→casa
- **Evidência forte de integração modal**

### 3. Pico Acadêmico às 16h
- 16h é o maior pico acadêmico (7.453 viagens)
- Coincide com horário de aula típico (16h-18h)
- **NÃO é 18h** (como no dataset SP completo)

### 4. Viagens Circulares nos Bandejões
- 1.717 viagens com mesma origem/destino
- Pode indicar:
  a) Problema de dados (bug no sistema)
  b) Pessoas que pegam bike, vão ao bandejão, voltam
  c) Viagens registradas incorretamente
- **Investigar mais!**

### 5. 52,8% de Viagens > 30 min
- Maioria das viagens é LONGA
- Sugere que bicicletas ficam estacionadas
- **NÃO é sistema de última milha**, é sistema de empréstimo de longa duração

---

## ⚠️ LIMITAÇÕES E PROBLEMAS ENCONTRADOS

### 1. IDs das Estações
- IDs no banco são diferentes dos IDs "lógicos" (242-260)
- Precisamos mapear manualmente:
  - 244 (lógico) → 56861 (banco)
  - 249 (lógico) → 38476 (banco)
  - etc.

### 2. Total de Viagens Diferente
- Esperado: 92.737 viagens (do arquivo ranking)
- Encontrado: 91.976 viagens
- Diferença: **761 viagens** (0,8%)
- Possível causa: estações duplicadas ou filtros diferentes

### 3. Viagens Internas
- Esperado: 63.598 (do relatório anterior)
- Encontrado: 61.082
- Diferença: **2.516 viagens** (4,0%)

### 4. Durações Absurdas
- Máximo: 111.013 minutos = **77 dias**!
- Sugere problemas no sistema de devolução
- **Filtrar outliers** antes de calcular média

---

## 🎯 PRÓXIMOS PASSOS

### Para a Monografia (Seção 5.8)

1. **Substituir análises anteriores** por estas (dataset correto)

2. **Destacar diferenças** Campus vs SP:
   - Pico do campus: 16h-17h
   - Pico de SP: 18h
   - Campus tem uso mais concentrado em horários acadêmicos

3. **Incluir gráficos:**
   - `analise_11_campus_horarios_academicos.png` (Figura 5.X)
   - `analise_11_campus_mare_portais.png` (Figura 5.Y)
   - `analise_11_campus_duracao_viagens.png` (Figura 5.Z)

4. **Usar MEDIANA** (33,7 min) em vez de média (198,5 min)

5. **Destacar** padrão "maré" no Metrô Butantã:
   - Entrada: 7h (saldo +453)
   - Saída: 17h (saldo -522)

6. **Mencionar** viagens circulares nos bandejões (investigação futura)

---

## 📧 RESUMO EXECUTIVO

**Análises refetas com sucesso** usando dataset exclusivo do campus (91.976 viagens).

**Principais descobertas:**
- ✅ Pico acadêmico às 16h (não 18h)
- ✅ Padrão "maré" claro no Metrô Butantã
- ✅ Duração mediana de 33,7 min (transporte entre unidades)
- ✅ 52,8% das viagens > 30 min (não é última milha)
- ⚠️ 1.717 viagens circulares no Bandejão Central (investigar)

**Tempo de execução:** 18,1 segundos

**Todos os gráficos e dados prontos para inclusão na monografia!** 🎓📚🚴

---

**Última atualização:** 13/11/2025 23:20h  
**Autor:** GitHub Copilot + Gabriel
