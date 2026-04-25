import json
import os
from datetime import datetime

import pandas as pd
from api_extract import extrair_dados_clima

OUTPUT_DIR = "data/raw"
CITIES_FILE = "data/cities.csv"


def criar_pasta_se_nao_existir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def gerar_nome_arquivo(cidade: str):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    cidade_formatada = (
        cidade.lower()
        .replace(" ", "_")
        .replace("ã", "a")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )

    return f"weather_{cidade_formatada}_{timestamp}.json"


def carregar_cidades():
    """
    Lê o arquivo CSV com as cidades.
    """
    df = pd.read_csv(CITIES_FILE)
    return df.to_dict(orient="records")


def salvar_json(data: dict, path: str):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    print("Iniciando coleta de dados meteorológicos...")

    criar_pasta_se_nao_existir(OUTPUT_DIR)

    cidades = carregar_cidades()

    for cidade in cidades:
        data = extrair_dados_clima(
            latitude=cidade["latitude"],
            longitude=cidade["longitude"],
            cidade=cidade["city"]
        )

        filename = gerar_nome_arquivo(cidade["city"])
        filepath = os.path.join(OUTPUT_DIR, filename)

        salvar_json(data, filepath)

        print(f"Arquivo salvo: {filename}")

    print("Coleta finalizada.")


if __name__ == "__main__":
    main()