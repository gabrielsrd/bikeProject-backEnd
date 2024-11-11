python3 manage.py runserver

endpoint: http://localhost:8000/api/ciclovias/

it serves a geo-json.


### README

## Projeto Backend (Português)

**Título**: API Backend para Análise de Ciclofaixas e Estações de Bicicletas Compartilhadas em São Paulo

**Descrição**: Este projeto backend em Python utiliza Django para fornecer uma API que realiza cálculos e processa dados geográficos, disponibilizando-os no formato GeoJSON para o frontend da aplicação web. A API serve informações sobre:
- Ciclofaixas (faixas dedicadas para bicicletas) em São Paulo
- Localizações das estações de bicicletas compartilhadas da Tembici
- Áreas que necessitam de mais infraestrutura cicloviária

A API é projetada para que organizações e empresas possam obter insights sobre o uso de bicicletas na cidade, incluindo as rotas mais utilizadas e as necessidades de infraestrutura.

**Funcionalidades**:
- **API RESTful**: fornece dados sobre ciclofaixas, estações de bicicletas e zonas prioritárias em São Paulo.
- **Cálculos Geográficos**: processa e organiza dados geoespaciais para o frontend.
- **Formato GeoJSON**: fornece dados de forma otimizada para mapeamento interativo.

**Tecnologias Utilizadas**:
- **Backend**: Django, Python
- **Banco de Dados**: SQLite (ou outro banco de dados Django-compatible)
- **Formatos de Dados**: GeoJSON para dados geoespaciais

**Como Executar o Projeto**:
1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/nomerepositorio-backend.git
   ```
2. Acesse o diretório do projeto:
   ```bash
   cd nomerepositorio-backend
   ```
3. Instale as dependências do Python:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute a aplicação:
   ```bash
   python3 manage.py runserver
   ```
5. Certifique-se de que o backend está rodando antes de carregar o frontend para que os dados GeoJSON possam ser servidos corretamente.

6. Endpoint: http://localhost:8000/api/ciclovias/
---

## Backend Project (English)

**Title**: Backend API for Analyzing Bike Lanes and Shared Bike Stations in São Paulo

**Description**: This backend project, written in Python and powered by Django, provides an API that performs calculations and processes geographical data, serving it in GeoJSON format to the web application frontend. The API delivers information on:
- Bike lanes in São Paulo
- Locations of Tembici shared bike stations
- Zones needing additional bike infrastructure

The API is designed to help organizations and businesses gain insights on bike usage in the city, including frequently traveled routes and infrastructure needs.

**Features**:
- **RESTful API**: serves data on bike lanes, bike-sharing stations, and priority zones in São Paulo.
- **Geographical Calculations**: processes and organizes geospatial data for the frontend.
- **GeoJSON Format**: optimizes data output for interactive mapping.

**Technologies Used**:
- **Backend**: Django, Python
- **Database**: SQLite (or other Django-compatible database)
- **Data Formats**: GeoJSON for geospatial data

**How to Run the Project**:
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/repositoryname-backend.git
   ```
2. Go to the project directory:
   ```bash
   cd repositoryname-backend
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python3 manage.py runserver
   ```
5. Ensure the backend is running before loading the frontend to enable the proper serving of GeoJSON data.77

6. Endpoint: http://localhost:8000/api/ciclovias/
