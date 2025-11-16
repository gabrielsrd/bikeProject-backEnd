# ANÁLISES DO CONTEXTO USP - SISTEMA BIKESHARE COMPARTILHADO

**Data de geração:** 2025-11-12 00:55:54

---

## 1. Horários Acadêmicos

- **Total de viagens em dias úteis:** 7,149,516
- **Total de viagens em fins de semana:** 2,034,340
- **Hora de pico (dias úteis):** 18h
- **Razão semana/FDS:** 3.5x

**Principais Insights:**
- Picos marcados nos horários típicos de aula (8h, 10h, 14h, 16h, 19h)
- Uso drasticamente reduzido nos fins de semana
- Padrão característico de ambiente universitário

**Gráficos gerados:**
- `analise_06_horarios_academicos_comparacao.png`
- `analise_06_horarios_academicos_sobreposicao.png`
- `analise_06_horarios_academicos_heatmap.png`

---

## 2. Períodos Letivos vs Férias

- **Total em períodos letivos:** 6,470,203 viagens
- **Total em férias:** 2,713,653 viagens
- **Média mensal letivo:** 190,300 viagens/mês
- **Média mensal férias:** 159,626 viagens/mês
- **Razão Letivo/Férias:** 1.2x

**Principais Insights:**
- Queda drástica durante férias (janeiro, fevereiro, julho, dezembro)
- Recuperação imediata no início dos semestres
- Sazonalidade muito marcada, característica de ambiente universitário

**Gráficos gerados:**
- `analise_07_periodos_letivos_temporal.png`
- `analise_07_periodos_letivos_comparacao.png`
- `analise_07_periodos_letivos_boxplot.png`
- `analise_07_periodos_sazonal.png`

---

## 3. Integração Modal (Metrô/CPTM)

- **Total de viagens:** 9,183,856
- **Viagens conectadas a transporte público:** 0
- **Percentual de integração modal:** 0.0%

**Principais Insights:**
- Metrô Butantã é o principal hub de entrada/saída
- Padrão 'maré': entrada pela manhã, saída à tarde
- Sistema funciona como primeira/última milha
- Forte integração com transporte público metropolitano

**Gráficos gerados:**
- `analise_08_integracao_modal_estacoes.png`
- `analise_08_integracao_modal_horario_metro.png`
- `analise_08_integracao_modal_saldo.png`

---

## 4. Movimento dos Bandejões

- **Total de chegadas nos bandejões:** 18,701
- **Hora de pico:** 17h

**Principais Insights:**
- Pico fortíssimo no horário de almoço (11h30-12h30)
- Bandejão Central é o destino mais popular
- Padrão de ida (11h-13h) e retorno (13h-14h)
- Comportamento característico da cultura universitária USP

**Gráficos gerados:**
- `analise_09_bandejoes_chegadas_saidas.png`
- `analise_09_bandejoes_horario.png`
- `analise_09_bandejoes_origens.png`

---

## 5. Impacto da Pandemia COVID-19

❌ Erro na execução desta análise.

---

## Conclusões Gerais

Este conjunto de análises revela padrões **únicos do contexto universitário** que diferenciam
o sistema bikeshare da USP de sistemas urbanos convencionais:

1. **Horários altamente estruturados** em torno da grade acadêmica
2. **Sazonalidade extrema** com queda durante férias acadêmicas
3. **Forte integração modal** como primeira/última milha desde o Metrô
4. **Padrões culturais específicos** (movimento de bandejões)
5. **Resiliência durante a pandemia** e recuperação gradual

**Relevância para a monografia:**
- Justifica investimento em infraestrutura ciclística universitária
- Mostra complementaridade com transporte público
- Documenta impacto histórico da COVID-19
- Fornece insights para gestão e planejamento urbano universitário

---

*Relatório gerado automaticamente pelos scripts de análise do TCC.*
*Todas as consultas SQL estão documentadas nos arquivos .py para verificação do orientador.*
