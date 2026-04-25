import os
import pandas as pd

# arquivo processado gerado pelo script 03
INPUT_FILE = "data/processed/weather_hourly.parquet"

# arquivo final da camada analítica
OUTPUT_FILE = "data/processed/weather_analytics_by_city.csv"


def validar_arquivo(path: str):
    """
    Verifica se o arquivo processado existe antes de iniciar a análise.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")


def criar_tabela_analitica():
    """
    Cria uma tabela analítica agregada por cidade.

    A tabela resume indicadores meteorológicos principais:
    - temperatura média
    - temperatura mínima
    - temperatura máxima
    - precipitação total
    - velocidade média do vento
    - total de registros horários
    """
    df = pd.read_parquet(INPUT_FILE)

    analytics = (
        df.groupby("city")
        .agg(
            temperatura_media=("temperature_2m", "mean"),
            temperatura_minima=("temperature_2m", "min"),
            temperatura_maxima=("temperature_2m", "max"),
            precipitacao_total=("precipitation", "sum"),
            vento_medio=("wind_speed_10m", "mean"),
            total_registros=("city", "count")
        )
        .reset_index()
    )

    # arredonda os valores numéricos para facilitar leitura
    analytics["temperatura_media"] = analytics["temperatura_media"].round(2)
    analytics["temperatura_minima"] = analytics["temperatura_minima"].round(2)
    analytics["temperatura_maxima"] = analytics["temperatura_maxima"].round(2)
    analytics["precipitacao_total"] = analytics["precipitacao_total"].round(2)
    analytics["vento_medio"] = analytics["vento_medio"].round(2)

    analytics.to_csv(OUTPUT_FILE, index=False)

    print(f"Tabela analítica salva em: {OUTPUT_FILE}")
    print(analytics)


def main():
    """
    Pipeline analítico:

    1. Valida se a camada processed existe
    2. Lê os dados processados
    3. Agrega indicadores por cidade
    4. Salva a camada analítica
    """

    print("Iniciando criação da camada analítica...")

    validar_arquivo(INPUT_FILE)
    criar_tabela_analitica()

    print("Camada analítica criada com sucesso.")


if __name__ == "__main__":
    main()