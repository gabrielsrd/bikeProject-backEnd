# BikeProject Backend

Backend Django para analise de dados de bicicletas compartilhadas (Bike Sampa) em Sao Paulo.

TCC - Gabriel Silva - IME-USP 2024/2025

## Sobre

Sistema que analisa ~9 milhoes de viagens de bicicleta entre 2018-2022, com foco no campus da USP.

Dados do projeto BikeScience (Prof. Dr. Fabio Kon - IME/USP).

## Como rodar

```bash
# ativar ambiente virtual
source venv/bin/activate

# rodar servidor
python manage.py runserver
```

API disponivel em: http://localhost:8000/api/

## Instalacao do zero

```bash
# criar ambiente
python3 -m venv venv
source venv/bin/activate

# instalar dependencias
pip install -r requirements.txt

# criar banco
python manage.py migrate

# importar dados (demora bastante)
python manage.py import_trips dataRaw/consolidated_tembici_data_COMPLETO.csv
```

## Processar dados brutos

Se precisar processar os arquivos ZIP originais:

```bash
python3 scripts/consolidate_tembici_COMPLETO.py
```

Isso gera o CSV consolidado em `dataRaw/consolidated_tembici_data_COMPLETO.csv`.

## Endpoints principais

- `/api/estacoes/` - estacoes em GeoJSON
- `/api/ciclovias/` - ciclovias de SP
- `/api/station_histogram/` - histograma de viagens por estacao
- `/api/trip_flows/` - fluxos entre estacoes

## Tecnologias

- Django 5.0
- Django REST Framework
- Pandas
- SQLite
- GeoPandas

## Estrutura

```
bikeProject-backEnd/
├── ciclovias/           # app principal
├── scripts/             # processamento de dados
├── dataRaw/             # dados brutos
├── geojsons/            # dados geoespaciais
├── analises_monografia/ # scripts de analise para TCC
└── db.sqlite3          # banco de dados
```

## Analises

Scripts de analise em `analises_monografia/`:

```bash
cd analises_monografia
./executar_todas_analises.sh
```

Gera graficos e estatisticas para a monografia.

## Creditos

Gabriel da Silva Alves
IME-USP
Orientador: Prof. Dr. Fabio Kon
