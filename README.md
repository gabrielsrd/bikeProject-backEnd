# 🚲 Bike Project - Backend API

Backend Django para análise de dados de bicicletas compartilhadas (Tembici) em São Paulo, fornecendo API RESTful com dados geográficos e análise de viagens.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Quick Start](#-quick-start)
- [Setup Completo](#️-setup-completo)
- [API Endpoints](#-api-endpoints)
- [Processamento de Dados](#-processamento-de-dados)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tecnologias](#-tecnologias)

---

## 🎯 Visão Geral

Este projeto analisa **~11 milhões de viagens** de bicicletas compartilhadas (2018-2023) e fornece:

- **API RESTful** com dados de estações, viagens e ciclofaixas
- **Análise geoespacial** de hotzones e padrões de uso
- **Histogramas** de uso por estação
- **Filtros personalizados** (ex: estações USP)

**Fontes de Dados:**
- 🚴 Viagens Tembici: Projeto BikeScience (Prof. Dr. Fabio Kon - IME/USP)
- 🗺️ Ciclofaixas: Portal [GeoSampa](https://geosampa.prefeitura.sp.gov.br/)
- 📍 Estações: Dados Tembici via BikeScience

---

## ⚡ Quick Start

```bash
# 1. Clone e entre no diretório
cd /home/gbiel/gabriel/usp/tcc/bikeProject-backEnd

# 2. Ative o ambiente virtual
source venv/bin/activate

# 3. Execute o servidor
python manage.py runserver

# ✅ Acesse: http://localhost:8000/api/
```

**Pré-requisitos:** Python 3.12+, dados já processados em `db.sqlite3`

---

## 🛠️ Setup Completo

### 1️⃣ Configurar Ambiente

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2️⃣ Processar Dados (Primeira vez)

**Se você NÃO tem o `dataRaw/consolidated_tembici_data.csv`:**

```bash
# Consolida ~45 CSVs dos ZIPs em um único arquivo
python3 scripts/consolidate_tembici_data.py
```

⏱️ **Tempo:** 30-90 minutos  
📊 **Output:** `dataRaw/consolidated_tembici_data.csv` (~1.9GB, 11M+ registros)

**Formato do CSV consolidado:**
```csv
trip_id,duration_seconds,initial_station_name,start_time,final_station_name,end_time,birth_year,initial_station_latitude,initial_station_longitude,final_station_latitude,final_station_longitude
```

📖 **Guia completo:** [GUIA_PROCESSAMENTO_DADOS.md](GUIA_PROCESSAMENTO_DADOS.md)

### 3️⃣ Criar Banco de Dados

```bash
# Criar tabelas no SQLite
python manage.py migrate
```

### 4️⃣ Importar Dados

**Opção A: Importar TODOS os dados**
```bash
python manage.py import_trips dataRaw/consolidated_tembici_data.csv
```

**Opção B: Filtrar por estações (ex: USP - IDs 238-261)**
```bash
python manage.py import_trips dataRaw/consolidated_tembici_data.csv --station-id-min 238 --station-id-max 261
```

⏱️ **Tempo:** 20-60 minutos  
📊 **Output:** `db.sqlite3` com tabelas `Station` e `Trip`

### 5️⃣ Executar Servidor

```bash
python manage.py runserver

# Ou para acesso externo:
python manage.py runserver 0.0.0.0:8000
```

---

## 🌐 API Endpoints

Após executar o servidor (`http://localhost:8000`):

### Dados de Banco de Dados (SQLite)

| Endpoint | Descrição | Exemplo |
|----------|-----------|---------|
| `/api/station_histogram/` | Histograma de viagens por estação | Retorna contagem de viagens iniciadas/finalizadas |
| `/api/trip_flows/` | Análise de fluxos entre estações | Origem → Destino com contagens |
| `/api/stations/` | Lista de estações | Dados de todas as estações importadas |
| `/api/trips/` | Lista de viagens | Dados de viagens importadas |

### Dados Geoespaciais (GeoJSON)

| Endpoint | Descrição | Formato |
|----------|-----------|---------|
| `/api/ciclovias/` | Ciclofaixas de São Paulo | GeoJSON |
| `/api/estacoes/` | Estações Tembici | GeoJSON |
| `/api/hotzones/` | Zonas de alta demanda | GeoJSON |

### Exemplos de Uso

```bash
# Histograma de estações
curl http://localhost:8000/api/station_histogram/

# Fluxos entre estações
curl http://localhost:8000/api/trip_flows/

# Ciclofaixas (GeoJSON)
curl http://localhost:8000/api/ciclovias/
```

**Admin Django:** `http://localhost:8000/admin/`

---

## 📊 Processamento de Dados

### Scripts Disponíveis

| Script | Função | Uso |
|--------|--------|-----|
| `consolidate_tembici_data.py` | ⭐ Consolida CSVs (recomendado) | `python3 scripts/consolidate_tembici_data.py` |
| `consolidate_tembici_simple.py` | Versão simplificada | Para datasets menores |
| `consolidate_tembici_cleaned.py` | Com limpeza de dados | Remove duplicatas/inválidos |
| `efficient_tembici_consolidator.py` | Otimizado memória | Para máquinas com pouca RAM |

### Management Commands

```bash
# Importar viagens do CSV
python manage.py import_trips <caminho_csv> [opções]

# Opções:
#   --station-id-min <id>  # ID mínimo da estação
#   --station-id-max <id>  # ID máximo da estação
#   --batch-size <n>       # Tamanho do lote (padrão: 10000)

# Exemplo: Importar apenas estações USP (238-261)
python manage.py import_trips dataRaw/consolidated_tembici_data.csv \
  --station-id-min 238 --station-id-max 261
```

### Fluxo de Dados

```
📦 ZIPs (7 arquivos)
  ├── 2018-2020 (formato antigo)
  └── 2021-2023 (formato novo + coordenadas)
         ↓
📝 consolidate_tembici_data.py
  ├── Extrai ZIPs
  ├── Normaliza formatos
  └── Gera CSV único
         ↓
📊 consolidated_tembici_data.csv (~1.9GB, 11M+ registros)
         ↓
🗄️ import_trips (Django command)
  ├── Cria estações (Station)
  ├── Cria viagens (Trip)
  └── Aplica filtros (opcional)
         ↓
💾 db.sqlite3 (SQLite database)
         ↓
🌐 API Django REST
```

---

## 📁 Estrutura do Projeto

```
bikeProject-backEnd/
├── 📋 README.md                    # Este arquivo
├── 📖 GUIA_PROCESSAMENTO_DADOS.md  # Guia detalhado de processamento
├── ⚙️ manage.py                    # Django management
├── 🔧 requirements.txt             # Dependências Python
├── 💾 db.sqlite3                   # Banco de dados SQLite
│
├── 🗂️ ciclovias/                   # App principal Django
│   ├── models.py                   # Models: Station, Trip
│   ├── views.py                    # API views
│   ├── urls.py                     # Rotas da API
│   └── management/commands/
│       └── import_trips.py         # Command para importar dados
│
├── 📊 dataRaw/                     # Dados brutos (ignorado no git)
│   ├── Tembici-SaoPaulo/          # ZIPs com CSVs (2018-2023)
│   └── consolidated_tembici_data.csv  # CSV consolidado
│
├── 🗺️ geojsons/                    # Dados geoespaciais
│   ├── ciclovia.geojson           # Ciclofaixas SP
│   ├── estacoes.geojson           # Estações Tembici
│   └── hotzones.geojson           # Zonas de alta demanda
│
├── 🛠️ scripts/                     # Scripts de processamento
│   ├── consolidate_tembici_data.py           # ⭐ Consolidação principal
│   ├── consolidate_tembici_simple.py         # Versão simplificada
│   ├── consolidate_tembici_cleaned.py        # Com limpeza
│   ├── efficient_tembici_consolidator.py     # Otimizado
│   ├── xlsToGeoJson.py                       # Excel → GeoJSON
│   ├── userTripsHotzonesKDEs.py              # Análise KDE
│   └── stationsHistogram.py                  # Histogramas
│
└── 🐍 venv/                        # Ambiente virtual (ignorado no git)
```

---

## 🔧 Tecnologias

### Backend
- **Django 5.0.6** - Web framework
- **Django REST Framework 3.15** - API REST
- **SQLite** - Banco de dados

### Processamento de Dados
- **Pandas 2.2.2** - Manipulação de dados
- **NumPy 1.26.4** - Computação numérica
- **GeoPandas** - Dados geoespaciais
- **Shapely** - Geometrias
- **tqdm** - Progress bars

### Frontend (Separado)
- Repositório: [bikeProject-frontEnd](https://github.com/gabrielsrd/bikeProject-frontEnd)

---

## 🐳 Docker (Opcional)

### Executar com Docker

```bash
# Construir imagem
docker build -t bikeproject-backend .

# Executar container
docker run -p 8000:8000 bikeproject-backend
```

### Docker Compose

```bash
# Iniciar serviços
docker-compose up

# Parar serviços
docker-compose down
```

**Arquivos disponíveis:**
- `docker-compose.yml` - Configuração padrão
- `docker-compose.simple.yml` - Versão simplificada
- `docker-compose.light.yml` - Versão leve
- `docker-compose.sqlite.yml` - Com SQLite persistente

---

## 🧪 Testes

```bash
# Testar fluxos de viagens
python test_trip_flows.py

# Testar endpoints da API
python test_endpoints.py

# Testar importação
python test_django.py
```

---

## 📚 Documentação Adicional

- **[GUIA_PROCESSAMENTO_DADOS.md](GUIA_PROCESSAMENTO_DADOS.md)** - Guia completo de processamento de dados
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Configuração Docker detalhada
- **[DOCKER_USAGE.md](DOCKER_USAGE.md)** - Como usar Docker
- **[CSV_TO_DATABASE_PLAN.md](CSV_TO_DATABASE_PLAN.md)** - Plano de importação de dados

---

## 🤝 Créditos

**Desenvolvido por:** Gabriel Alves  
**Instituição:** IME-USP (Instituto de Matemática e Estatística - Universidade de São Paulo)  
**Orientador:** Prof. Dr. Fabio Kon

### Fontes de Dados

- **Viagens Tembici:** [Projeto BikeScience](https://www.ime.usp.br/~kon/bikesampa/) (IME-USP)
- **Ciclofaixas:** [GeoSampa](https://geosampa.prefeitura.sp.gov.br/) - Prefeitura de São Paulo
- **Metadados:** [Portal de Metadados GeoSampa](https://metadados.geosampa.prefeitura.sp.gov.br/)

---

## 📄 Licença

Este projeto é parte de um trabalho acadêmico da USP.

---

## 🔗 Links Relacionados

- **Frontend:** [bikeProject-frontEnd](https://github.com/gabrielsrd/bikeProject-frontEnd)
- **BikeScience:** [Projeto BikeScience - IME/USP](https://www.ime.usp.br/~kon/bikesampa/)
- **GeoSampa:** [Portal de Dados Abertos SP](https://geosampa.prefeitura.sp.gov.br/)

---

**Última atualização:** Novembro 2025