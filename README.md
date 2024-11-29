

# Projeto Backend - Análise de Ciclofaixas e Estações de Bicicletas em São Paulo

**Descrição**:  
Este projeto backend utiliza Django para fornecer uma API RESTful que processa e serve dados geográficos no formato GeoJSON. O foco está na análise de ciclofaixas, estações de bicicletas compartilhadas e áreas de alta demanda de infraestrutura cicloviária (hotzones).  

Os dados fornecidos são baseados em fontes confiáveis, como os dados abertos da Prefeitura de São Paulo e o projeto BikeScience do Prof. Dr. Fabio Kon (IME-USP). A aplicação está configurada para fornecer insights e otimizar a tomada de decisão em relação ao uso de bicicletas na cidade.  

---

## **Funcionalidades**

- **API RESTful**:  
  Fornece dados de ciclofaixas, estações de bicicletas compartilhadas e zonas prioritárias (hotzones).  
- **Processamento de Dados Geoespaciais**:  
  Utiliza scripts para tratar dados de shapefiles, arquivos CSV e Excel, transformando-os em GeoJSON otimizados para consumo.  
- **Cálculos e Otimizações**:  
  Inclui cálculos como distância entre estações e ciclofaixas, identificação de zonas de alta demanda (120 mil viagens analisadas) e agregação de dados geográficos.  

---

## **Endpoints Disponíveis**

1. **Ciclofaixas**  
   - **Descrição:** Retorna os dados de ciclofaixas da cidade de São Paulo.  
   - **Endpoint:** `http://localhost:8000/api/ciclovias/`  
   - **Formato:** GeoJSON  

2. **Estações de Bicicletas**  
   - **Descrição:** Fornece informações sobre as localizações das estações de bicicletas compartilhadas da Tembici.  
   - **Endpoint:** `http://localhost:8000/api/estacoes/`  
   - **Formato:** GeoJSON  

3. **Hotzones**  
   - **Descrição:** Apresenta zonas prioritárias de infraestrutura cicloviária, baseadas em análise de aproximadamente 120 mil viagens.  
   - **Endpoint:** `http://localhost:8000/api/hotzones/`  
   - **Formato:** GeoJSON  

---

## **Fontes de Dados**

- **Ciclofaixas:** Dados abertos da Prefeitura de São Paulo, disponíveis no portal [GeoSampa](https://geosampa.prefeitura.sp.gov.br/).  
  - Formatos: Shapefile (SAD69, SIRGAS)  
  - Metadados: Disponíveis [aqui](https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/por/catalog.search#/metadata/5d973631-65e5-447d-ab38-e5fb6b07a67b).  

- **Estações de Bicicletas:** Dados fornecidos pelo projeto BikeScience, liderado pelo Prof. Dr. Fabio Kon (IME-USP), em colaboração com a Tembici.  

- **Viagens (Hotzones):** Dados anonimizados de 120 mil viagens de bicicletas compartilhadas, também fornecidos pelo BikeScience.  

---

## **Tecnologias Utilizadas**

- **Backend:** Django, Python   
- **Processamento Geoespacial:** GeoPandas, Shapely, Pandas, SciPy, GeoPy  
- **Formato de Dados:** GeoJSON  

---

## **Como Executar o Projeto**

1. Instale as dependências do Python:
   ```bash
   pip install -r requirements.txt
   ```


2. Execute a aplicação:
   ```bash
   python manage.py runserver
   ```

3. Acesse os endpoints:
   - Ciclofaixas: `http://localhost:8000/api/ciclovias/`  
   - Estações: `http://localhost:8000/api/estacoes/`  
   - Hotzones: `http://localhost:8000/api/hotzones/`  

---

## **Scripts para Tratamento de Dados**

Os dados brutos foram processados utilizando scripts Python disponíveis na pasta `scripts/`. Abaixo estão os principais scripts:  

1. **`xlsToGeoJson.py`:**  
   Converte arquivos Excel (como `estacoes.xlsx`) para GeoJSON.  

2. **`addIdCiclovia.py`:**  
   Adiciona IDs únicos às ciclovias no formato GeoJSON.  

3. **`calculateDistanciaEstacacaoCiclovia.py`:**  
   Calcula distâncias entre as estações de bicicletas e as ciclofaixas mais próximas.  

4. **`userTripsHotzonesKDEs.py`:**  
   Analisa 120 mil viagens para identificar zonas de alta demanda (hotzones) usando análise KDE.  

---

## **Estrutura do Repositório**

```plaintext
├── README.md              # Documentação do projeto
├── ciclovias              # App principal no Django
│   ├── models.py          # Modelos do Django
│   ├── views.py           # Views que fornecem GeoJSON
│   ├── urls.py            # Rotas do app
├── geojsons               # Dados geoespaciais processados
│   ├── ciclovia.geojson
│   ├── estacoes.geojson
│   └── hotzones.geojson
├── dataRaw                # Dados brutos
├── dataClean              # Dados tratados 
├── scripts                # Scripts de pré-processamento
├── manage.py              # Comando principal do Django
├── db.sqlite3             # Banco de dados local
```

---

## **Observações Finais**

1. **Compatibilidade dos Dados:** Durante o pré-processamento, os shapefiles foram convertidos para GeoJSON para facilitar a leitura e integração com o front-end.  
2. **Zonas Prioritárias:** A análise das "hotzones" foi baseada em algoritmos de densidade por kernel (KDE).  
3. **FrontEnd** Link para o repositório: https://github.com/gabrielsrd/bikeProject-frontEnd 

