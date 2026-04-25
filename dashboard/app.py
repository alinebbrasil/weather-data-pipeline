import re
from datetime import datetime

import pandas as pd
import streamlit as st

# configuração da página do Streamlit
st.set_page_config(
    page_title="Weather Data Dashboard",
    layout="wide"
)

# caminho do arquivo processado gerado pelo pipeline
DATA_PATH = "data/processed/weather_hourly.parquet"


def extrair_timestamp_coleta(source_file: str):
    """
    Extrai o timestamp da coleta a partir do nome do arquivo JSON.
    """
    match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", source_file)

    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d_%H-%M-%S")

    return None


@st.cache_data
def carregar_dados(path: str) -> pd.DataFrame:
    """
    Carrega os dados processados do pipeline e prepara colunas para o dashboard.
    """
    df = pd.read_parquet(path)

    # garante que a coluna de data/hora esteja no formato correto
    df["datetime"] = pd.to_datetime(df["datetime"])

    # cria a coluna com o horário real da coleta
    df["collection_timestamp"] = df["source_file"].apply(extrair_timestamp_coleta)

    # renomeia colunas técnicas para nomes mais amigáveis no dashboard
    df = df.rename(columns={
        "city": "Capital",
        "datetime": "Data/Hora",
        "temperature_2m": "Temperatura (°C)",
        "precipitation": "Precipitação (mm)",
        "wind_speed_10m": "Vento (km/h)"
    })

    return df


# carregamento dos dados
df = carregar_dados(DATA_PATH)

# título principal
st.title("Weather Data Dashboard")

# descrição geral
st.write(
    "Dashboard para acompanhamento de dados meteorológicos de capitais brasileiras "
    "coletados via API Open-Meteo e processados por pipeline de dados."
)

# métricas gerais do dataset
st.subheader("Visão geral")

col1, col2, col3 = st.columns(3)

col1.metric("Total de registros", len(df))
col2.metric("Capitais monitoradas", df["Capital"].nunique())
col3.metric(
    "Última coleta",
    df["collection_timestamp"].max().strftime("%d/%m/%Y %H:%M:%S")
)

# identifica a coleta mais recente do pipeline
ultima_coleta = df["collection_timestamp"].max()

# filtra apenas os dados da última coleta
df_ultima_coleta = (
    df.sort_values("collection_timestamp")
    .groupby("Capital", as_index=False)
    .tail(168)
)

# para o mapa, usa a primeira previsão disponível de cada capital na última coleta
df_mapa = (
    df_ultima_coleta
    .sort_values("Data/Hora")
    .groupby("Capital")
    .head(1)
    .reset_index(drop=True)
)

# ordena capitais alfabeticamente para facilitar leitura na tabela
df_mapa = df_mapa.sort_values("Capital").reset_index(drop=True)

st.subheader("Mapa das capitais monitoradas")

# mapa simples usando latitude e longitude
st.map(
    df_mapa,
    latitude="latitude",
    longitude="longitude",
    size=80
)

# tabela-resumo das capitais
st.subheader("Resumo das capitais")

st.dataframe(
    df_mapa[[
        "Capital",
        "Temperatura (°C)",
        "Precipitação (mm)",
        "Vento (km/h)"
    ]]
)

# filtro por capital
st.subheader("Análise por capital")

capitais = sorted(df["Capital"].unique())

capital_selecionada = st.selectbox(
    "Selecione uma capital",
    capitais
)

# filtra a capital selecionada usando apenas a última coleta
df_capital = df_ultima_coleta[
    df_ultima_coleta["Capital"] == capital_selecionada
].copy()

# ordena por data/hora para garantir gráficos temporais corretos
df_capital = df_capital.sort_values("Data/Hora")

# cálculo dos indicadores da capital selecionada
temperatura_media = round(df_capital["Temperatura (°C)"].mean(), 2)
temperatura_maxima = round(df_capital["Temperatura (°C)"].max(), 2)
precipitacao_total = round(df_capital["Precipitação (mm)"].sum(), 2)
vento_medio = round(df_capital["Vento (km/h)"].mean(), 2)

# exibição dos indicadores
col1, col2, col3, col4 = st.columns(4)

col1.metric("Temperatura média (°C)", temperatura_media)
col2.metric("Temperatura máxima (°C)", temperatura_maxima)
col3.metric("Precipitação total (mm)", precipitacao_total)
col4.metric("Vento médio (km/h)", vento_medio)

# gráfico de temperatura
st.subheader("Previsão horária de temperatura (°C)")

st.line_chart(
    df_capital,
    x="Data/Hora",
    y="Temperatura (°C)"
)

# gráfico de precipitação
st.subheader("Previsão horária de precipitação (mm)")

st.line_chart(
    df_capital,
    x="Data/Hora",
    y="Precipitação (mm)"
)

# gráfico de vento
st.subheader("Previsão horária de vento (km/h)")

st.line_chart(
    df_capital,
    x="Data/Hora",
    y="Vento (km/h)"
)

# tabela detalhada da capital selecionada
st.subheader("Dados detalhados da capital selecionada")

st.dataframe(
    df_capital[[
        "Data/Hora",
        "Capital",
        "Temperatura (°C)",
        "Precipitação (mm)",
        "Vento (km/h)",
        "source_file"
    ]]
)