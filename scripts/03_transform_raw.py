import json
import os
import pandas as pd

# pasta onde estão os arquivos JSON brutos
INPUT_DIR = "data/raw"

# pasta onde os arquivos processados serão salvos
OUTPUT_DIR = "data/processed"

# arquivos finais da camada processed
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "weather_hourly.csv")
OUTPUT_PARQUET = os.path.join(OUTPUT_DIR, "weather_hourly.parquet")


def criar_pasta_se_nao_existir(path: str):
    """
    Cria a pasta de saída caso ela ainda não exista.
    """
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Pasta criada: {path}")


def listar_arquivos_json(input_dir: str):
    """
    Lista todos os arquivos JSON da camada raw.
    Cada arquivo representa uma coleta de dados meteorológicos.
    """
    arquivos = [
        arquivo for arquivo in os.listdir(input_dir)
        if arquivo.endswith(".json")
    ]

    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo JSON encontrado em data/raw.")

    return arquivos


def transformar_json_em_linhas(arquivos):
    """
    Transforma os arquivos JSON da API em formato tabular.

    Cada linha representa uma observação horária de clima para uma cidade.
    """
    linhas = []

    for arquivo in arquivos:
        caminho = os.path.join(INPUT_DIR, arquivo)

        with open(caminho, "r", encoding="utf-8") as file:
            dados = json.load(file)

        cidade = dados.get("city")
        latitude = dados.get("latitude")
        longitude = dados.get("longitude")

        hourly = dados.get("hourly", {})

        tempos = hourly.get("time", [])
        temperaturas = hourly.get("temperature_2m", [])
        precipitacoes = hourly.get("precipitation", [])
        ventos = hourly.get("wind_speed_10m", [])

        for i in range(len(tempos)):
            linhas.append({
                "city": cidade,
                "latitude": latitude,
                "longitude": longitude,
                "datetime": tempos[i],
                "temperature_2m": temperaturas[i],
                "precipitation": precipitacoes[i],
                "wind_speed_10m": ventos[i],
                "source_file": arquivo
            })

    return linhas


def salvar_tabela(linhas):
    """
    Salva os dados transformados em CSV e Parquet.

    CSV:
    - fácil para inspeção manual

    Parquet:
    - mais eficiente e mais comum em pipelines de dados
    """
    df = pd.DataFrame(linhas)

    # converte datetime para tipo data/hora
    df["datetime"] = pd.to_datetime(df["datetime"])

    df.to_csv(OUTPUT_CSV, index=False)
    df.to_parquet(OUTPUT_PARQUET, index=False)

    print(f"Arquivo CSV salvo em: {OUTPUT_CSV}")
    print(f"Arquivo Parquet salvo em: {OUTPUT_PARQUET}")
    print(f"Total de registros: {len(df)}")


def main():
    """
    Pipeline de transformação:

    1. Lê os arquivos JSON brutos
    2. Transforma os dados horários em formato tabular
    3. Salva a camada processed em CSV e Parquet
    """

    print("Iniciando transformação dos dados meteorológicos...")

    criar_pasta_se_nao_existir(OUTPUT_DIR)

    arquivos = listar_arquivos_json(INPUT_DIR)

    linhas = transformar_json_em_linhas(arquivos)

    salvar_tabela(linhas)

    print("Transformação concluída com sucesso.")


if __name__ == "__main__":
    main()