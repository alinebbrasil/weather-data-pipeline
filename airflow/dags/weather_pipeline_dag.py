from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

"""
DAG: weather_data_pipeline

Objetivo:
Orquestrar um pipeline de dados meteorológicos.

Etapas:
1. Coletar dados da API Open-Meteo
2. Salvar respostas brutas em JSON
3. Transformar JSONs em tabela processada
4. Criar camada analítica por cidade

Execução:
- A cada 30 minutos
- Com retry automático em caso de falha
"""

with DAG(
    dag_id="weather_data_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="*/30 * * * *",
    catchup=False,
    description="Pipeline de dados meteorológicos via API Open-Meteo",
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    },
) as dag:

    save_raw = BashOperator(
        task_id="save_raw_json",
        bash_command="cd /opt/airflow && python scripts/02_save_raw_json.py",
    )

    transform_raw = BashOperator(
        task_id="transform_raw",
        bash_command="cd /opt/airflow && python scripts/03_transform_raw.py",
    )

    create_analytics = BashOperator(
        task_id="create_analytics",
        bash_command="cd /opt/airflow && python scripts/04_create_analytics.py",
    )

    save_raw >> transform_raw >> create_analytics