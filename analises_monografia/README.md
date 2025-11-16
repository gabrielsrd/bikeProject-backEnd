# Analises TCC

Scripts para gerar graficos e estatisticas da monografia.

## Como usar

Executar tudo de uma vez:

```bash
./executar_todas_analises.sh
```

Ou rodar individual:

```bash
python3 01_verificar_dados.py
python3 02_analise_temporal.py
python3 03_analise_por_estacao.py
python3 04_analise_fluxos.py
python3 05_gerar_relatorio.py
```

## Scripts

- `01_verificar_dados.py` - estatisticas basicas
- `02_analise_temporal.py` - analise por hora/dia/mes
- `03_analise_por_estacao.py` - ranking de estacoes
- `04_analise_fluxos.py` - fluxos entre estacoes
- `05_gerar_relatorio.py` - gera relatorio final

## Saida

Graficos salvos em `resultados/graficos/`
CSVs com dados em `resultados/`

## Notas

Estacoes USP: IDs 242-260
Dados: 2018-2023
Graficos em alta resolucao (300 DPI)
