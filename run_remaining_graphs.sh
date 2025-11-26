#!/bin/bash
set -e

echo "Resuming graph generation..."

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 analises_monografia/10_analise_impacto_covid.py
python3 analises_monografia/11_analise_campus_completa.py
python3 analises_monografia/13_analise_fluxo_interno.py
python3 analises_monografia/14_analise_fluxo_entrada.py
python3 analises_monografia/15_analise_fluxo_saida.py
python3 analises_monografia/16_evolucao_temporal_campus.py
python3 analises_monografia/analise_viagens_circulares_usp.py
python3 analises_monografia/grafico_circulares_por_estacao.py

echo "All remaining graphs generated successfully!"
