# Weather Data Pipeline

Pipeline de dados meteorológicos com ingestão via API, processamento em camadas, armazenamento em banco de dados relacional, orquestração com Airflow e visualização interativa com Streamlit.

## Objetivo

Construir um pipeline completo de engenharia de dados simulando um cenário real de mercado, incluindo:

- Coleta de dados via API
- Processamento em múltiplas camadas
- Persistência em banco de dados PostgreSQL
- Orquestração com Apache Airflow
- Visualização de dados com Streamlit

## Arquitetura

```
API Open-Meteo
        ↓
02_save_raw_json.py
        ↓
data/raw (JSON)
        ↓
03_transform_raw.py
        ↓
data/processed (CSV / Parquet)
        ↓
05_load_to_postgres.py
        ↓
PostgreSQL (weather_db)
        ↓
04_create_analytics.py
        ↓
data/processed (analytics)
        ↓
Airflow (orquestração)
        ↓
Streamlit Dashboard
```

## Tecnologias utilizadas

- Python
- Pandas
- PostgreSQL
- SQLAlchemy
- Apache Airflow (Docker)
- Streamlit
- Open-Meteo API

## Estrutura do projeto

```
weather-data-pipeline/
│
├── airflow/
│   ├── dags/
│   │   └── weather_pipeline_dag.py
│   └── docker-compose.yml
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── cities.csv
│
├── dashboard/
│   └── app.py
│
├── scripts/
│   ├── api_extract.py
│   ├── 02_save_raw_json.py
│   ├── 03_transform_raw.py
│   ├── 04_create_analytics.py
│   └── 05_load_to_postgres.py
│
├── requirements.txt
└── README.md
```

## Fonte de dados

Os dados são obtidos através da API Open-Meteo:

https://open-meteo.com/

## Funcionamento do pipeline

### Ingestão (raw)

- Coleta dados meteorológicos por capital brasileira
- Utiliza arquivo `cities.csv` como fonte configurável
- Armazena respostas da API em formato JSON na camada raw

### Transformação (processed)

- Converte JSON em formato tabular
- Gera arquivos CSV e Parquet
- Padroniza tipos de dados e estrutura

### Carga (PostgreSQL)

- Envia os dados processados para o banco de dados
- Tabela criada: `weather_hourly`

### Camada analítica

- Gera agregações por capital:
  - temperatura média, mínima e máxima
  - precipitação total
  - velocidade média do vento

### Orquestração (Airflow)

O pipeline é automatizado com as seguintes etapas:

```
save_raw → transform_raw → load_to_postgres → create_analytics
```

Execução agendada a cada 30 minutos.

## Dashboard

O dashboard apresenta:

- Mapa das capitais monitoradas
- Ranking de temperatura
- Filtro por capital
- Indicadores:
  - temperatura média, mínima e máxima
  - precipitação total
  - vento médio
- Séries temporais:
  - temperatura
  - precipitação
  - vento

## Como executar o projeto

### Instalar dependências

```
pip install -r requirements.txt
```

### Executar pipeline local

```
python scripts/02_save_raw_json.py
python scripts/03_transform_raw.py
python scripts/04_create_analytics.py
python scripts/05_load_to_postgres.py
```

### Executar Airflow

```
cd airflow
docker-compose up
```

Acesse:

```
http://localhost:8080
```

O usuário e senha são exibidos no terminal na primeira execução ou podem ser recriados manualmente.

### Executar dashboard

```
python -m streamlit run dashboard/app.py
```

## Observações

- O Airflow é executado em container Docker
- A conexão com PostgreSQL dentro do Airflow utiliza o hostname do serviço:

```
postgres
```

- Em execução local, pode-se utilizar:

```
localhost
```

- Os dados são classificados como near real-time, sendo atualizados periodicamente pela API

## Possíveis melhorias

- Implementação de streaming com Kafka
- Modelagem dimensional (Star Schema)
- Integração com ferramentas de BI
- Deploy em ambiente cloud
- Exposição de API para consumo dos dados

## Autora

Aline Bastos Brasil  
Engenharia de Dados / Ciência de Dados
