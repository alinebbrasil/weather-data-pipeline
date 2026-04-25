import re
from datetime import datetime

import pandas as pd
import streamlit as st

# configuração da página
st.set_page_config(
    page_title="Weather Data Dashboard",
    layout="wide"
)

# caminho do arquivo processado gerado pelo pipeline
DATA_PATH = "data/processed/weather_hourly.parquet"


def extrair_timestamp_coleta(source_file: str):
    """
    Extrai o timestamp de coleta a partir do nome do arquivo JSON.
    """
    match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", source_file)

    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d_%H-%M-%S")

    return None


def carregar_dados(path: str) -> pd.DataFrame:
    """
    Carrega os dados processados do pipeline e prepara as colunas para o dashboard.
    """
    df = pd.read_parquet(path)

    # garante que a data/hora esteja no formato correto
    df["datetime"] = pd.to_datetime(df["datetime"])

    # cria coluna com o timestamp real da coleta
    df["collection_timestamp"] = df["source_file"].apply(extrair_timestamp_coleta)

    # renomeia colunas técnicas para nomes mais amigáveis
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

st.write(
    "Dashboard para acompanhamento de dados meteorológicos das capitais brasileiras "
    "coletados via API Open-Meteo e processados por pipeline de dados."
)

# visão geral
st.subheader("Visão geral")

col1, col2, col3 = st.columns(3)

col1.metric("Total de registros", len(df))
col2.metric("Capitais monitoradas", df["Capital"].nunique())
col3.metric(
    "Última coleta registrada",
    df["collection_timestamp"].max().strftime("%d/%m/%Y %H:%M:%S")
)

# mantém uma janela recente de previsões por capital
# isso evita problemas quando cada capital é coletada em segundos diferentes
df_ultimas_coletas = (
    df.sort_values("collection_timestamp")
    .groupby("Capital", as_index=False)
    .tail(168)
)

# para o mapa, usa a primeira previsão disponível de cada capital nessa janela
df_mapa = (
    df_ultimas_coletas
    .sort_values("Data/Hora")
    .groupby("Capital")
    .head(1)
    .sort_values("Capital")
    .reset_index(drop=True)
)

st.subheader("Mapa das capitais monitoradas")

# mapa simples com latitude e longitude
st.map(
    df_mapa,
    latitude="latitude",
    longitude="longitude",
    size=120
)

st.subheader("Resumo das capitais")

# tabela-resumo ordenada alfabeticamente
st.dataframe(
    df_mapa[[
        "Capital",
        "Temperatura (°C)",
        "Precipitação (mm)",
        "Vento (km/h)"
    ]].sort_values("Capital").reset_index(drop=True),
    use_container_width=True
)

# ranking de temperatura atual por capital
st.subheader("Ranking de temperatura por capital")

ranking_temperatura = (
    df_mapa[[
        "Capital",
        "Temperatura (°C)",
        "Precipitação (mm)",
        "Vento (km/h)"
    ]]
    .sort_values("Temperatura (°C)", ascending=False)
    .reset_index(drop=True)
)

st.dataframe(
    ranking_temperatura,
    use_container_width=True
)

# análise individual por capital
st.subheader("Análise por capital")

capitais = sorted(df["Capital"].unique())

capital_selecionada = st.selectbox(
    "Selecione uma capital",
    capitais
)

# filtra dados da capital selecionada
df_capital = df[df["Capital"] == capital_selecionada].copy()

# usa a janela mais recente da capital selecionada
df_capital = (
    df_capital
    .sort_values("collection_timestamp")
    .tail(168)
    .sort_values("Data/Hora")
)

# cálculo dos indicadores
temperatura_media = round(df_capital["Temperatura (°C)"].mean(), 2)
temperatura_maxima = round(df_capital["Temperatura (°C)"].max(), 2)
temperatura_minima = round(df_capital["Temperatura (°C)"].min(), 2)
precipitacao_total = round(df_capital["Precipitação (mm)"].sum(), 2)
vento_medio = round(df_capital["Vento (km/h)"].mean(), 2)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Temp. média (°C)", temperatura_media)
col2.metric("Temp. máxima (°C)", temperatura_maxima)
col3.metric("Temp. mínima (°C)", temperatura_minima)
col4.metric("Precipitação total (mm)", precipitacao_total)
col5.metric("Vento médio (km/h)", vento_medio)

# gráficos temporais
st.subheader("Previsão horária de temperatura (°C)")

st.line_chart(
    df_capital,
    x="Data/Hora",
    y="Temperatura (°C)"
)

st.subheader("Previsão horária de precipitação (mm)")

st.line_chart(
    df_capital,
    x="Data/Hora",
    y="Precipitação (mm)"
)

st.subheader("Previsão horária de vento (km/h)")

st.line_chart(
    df_capital,
    x="Data/Hora",
    y="Vento (km/h)"
)

# dados detalhados
st.subheader("Dados detalhados da capital selecionada")

st.dataframe(
    df_capital[[
        "Data/Hora",
        "Capital",
        "Temperatura (°C)",
        "Precipitação (mm)",
        "Vento (km/h)",
        "collection_timestamp",
        "source_file"
    ]],
    use_container_width=True
)