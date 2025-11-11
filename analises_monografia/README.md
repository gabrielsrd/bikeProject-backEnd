# Análises para Monografia - BikeScience USP

Este diretório contém scripts Python para geração de análises e gráficos para inclusão na monografia de TCC.

## 📋 Scripts Disponíveis

### 01_verificar_dados.py
**Descrição:** Verifica a estrutura do banco de dados e gera estatísticas básicas
- Total de viagens e estações
- Identificação de estações USP (IDs 242-260)
- Viagens internas vs externas
- Ranking de estações mais utilizadas
- Salva CSVs com estatísticas

**Saída:**
- `resultados/estacoes_usp_estatisticas.csv`
- `resultados/resumo_geral.csv`

**Uso:**
```bash
python3 01_verificar_dados.py
```

---

### 02_analise_temporal.py
**Descrição:** Analisa padrões temporais das viagens
- Distribuição por hora do dia
- Distribuição por dia da semana
- Distribuição por mês
- Evolução temporal (2018-2023)
- Comparação dias úteis vs fim de semana
- Impacto da pandemia COVID-19

**Saída:**
- Gráficos em `resultados/graficos/`
  - `viagens_por_hora.png`
  - `viagens_por_dia_semana.png`
  - `viagens_por_mes.png`
  - `evolucao_temporal_viagens.png`
  - `comparacao_util_fds_hora.png`
- CSVs correspondentes em `resultados/`

**Uso:**
```bash
python3 02_analise_temporal.py
```

---

### 03_analise_por_estacao.py
**Descrição:** Análise detalhada de cada estação USP
- Ranking completo de estações
- Balanço (saídas vs chegadas) por estação
- Padrão horário das top 5 estações
- Comparação por grupos de estações
- Heatmap estações vs hora do dia

**Saída:**
- Gráficos em `resultados/graficos/`
  - `ranking_estacoes_usp.png`
  - `balanco_estacoes_usp.png`
  - `top5_estacoes_padrao_horario.png`
  - `comparacao_grupos_estacoes.png`
  - `heatmap_estacoes_hora.png`
- CSVs correspondentes

**Uso:**
```bash
python3 03_analise_por_estacao.py
```

---

### 04_analise_fluxos.py
**Descrição:** Analisa fluxos entre estações
- Top 20 rotas mais frequentes
- Fluxos internos (USP→USP) vs externos (USP↔Fora)
- Matriz origem-destino completa
- Principais destinos por estação

**Saída:**
- Gráficos em `resultados/graficos/`
  - `top20_rotas_frequentes.png`
  - `fluxos_internos_externos.png`
  - `matriz_origem_destino_usp.png`
  - `principais_destinos_top5_estacoes.png`
- CSVs com dados completos de fluxos

**Uso:**
```bash
python3 04_analise_fluxos.py
```

---

### 05_gerar_relatorio.py
**Descrição:** Gera relatório consolidado com todas as estatísticas
- Coleta todas as estatísticas principais
- Gera comandos LaTeX (`\newcommand`) para inserção direta na monografia
- Gera relatório em texto plano

**Saída:**
- `resultados/estatisticas_monografia.tex` - Comandos LaTeX
- `resultados/relatorio_completo.txt` - Relatório legível

**Uso:**
```bash
python3 05_gerar_relatorio.py
```

**Como usar no LaTeX:**
```latex
% No preâmbulo do tese.tex
\input{../bikeProject-backEnd/analises_monografia/resultados/estatisticas_monografia.tex}

% No texto
O campus da USP possui \totalEstacoesUSP{} estações de bicicletas compartilhadas,
que registraram \totalViagensUSP{} viagens entre \dataPrimeiraViagem{} e \dataUltimaViagem{}.
```

---

## 🚀 Executar Todas as Análises

Para executar todos os scripts de uma vez:

```bash
./executar_todas_analises.sh
```

Ou manualmente:
```bash
python3 01_verificar_dados.py && \
python3 02_analise_temporal.py && \
python3 03_analise_por_estacao.py && \
python3 04_analise_fluxos.py && \
python3 05_gerar_relatorio.py
```

---

## 📊 Estrutura de Saída

```
analises_monografia/
├── resultados/
│   ├── graficos/              # Todos os gráficos em PNG (alta resolução)
│   │   ├── viagens_por_hora.png
│   │   ├── ranking_estacoes_usp.png
│   │   ├── top20_rotas_frequentes.png
│   │   └── ... (outros gráficos)
│   │
│   ├── *.csv                  # Dados brutos em CSV
│   ├── estatisticas_monografia.tex  # Comandos LaTeX
│   └── relatorio_completo.txt       # Relatório em texto
│
└── *.py                       # Scripts de análise
```

---

## 📝 Notas Importantes

### Estações USP
As estações do campus USP Butantã têm IDs entre **242 e 260**:
- 242 - IME
- 244 - Metrô Butantã
- 246 - Portão CPTM
- 249 - Bandejão Central
- (e outras...)

### Viagens USP
Consideramos "viagens USP" aquelas onde:
- **Origem OU destino** está no campus (IDs 242-260)

Subdividimos em:
- **Internas:** Origem E destino no campus
- **Externas:** Uma ponta fora do campus

### Período dos Dados
Os dados abrangem aproximadamente **2018 a 2023**, permitindo análise:
- Pré-pandemia (até 2019)
- Durante pandemia (2020-2021)
- Pós-pandemia (2022+)

### Qualidade dos Gráficos
Todos os gráficos são salvos em **alta resolução (300 DPI)** para garantir qualidade na impressão da monografia.

---

## 🔧 Requisitos

- Python 3.8+
- Django 5.0+
- pandas
- matplotlib
- seaborn
- numpy

Todos já instalados no ambiente virtual do projeto backend.

---

## ❓ Troubleshooting

### Erro: "No module named 'ciclovias'"
Execute os scripts **dentro do diretório backend** com o ambiente virtual ativado:
```bash
cd /home/gbiel/gabriel/usp/tcc/bikeProject-backEnd
source venv/bin/activate
python3 analises_monografia/01_verificar_dados.py
```

### Erro: "Permission denied"
Torne os scripts executáveis:
```bash
chmod +x analises_monografia/*.py
```

### Gráficos não aparecem
Os gráficos são salvos em arquivo (não exibidos na tela). Verifique o diretório `resultados/graficos/`.

---

## 📧 Contato

**Autor:** Gabriel da Silva Alves  
**Orientador:** Prof. Dr. Fabio Kon  
**Instituição:** IME-USP

---

**Última atualização:** Novembro 2025
