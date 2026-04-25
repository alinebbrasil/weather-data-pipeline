import requests


def extrair_dados_clima(latitude: float, longitude: float, cidade: str) -> dict:
    """
    Consulta a API Open-Meteo para obter previsão horária de uma cidade.

    Parâmetros:
        latitude: latitude da cidade
        longitude: longitude da cidade
        cidade: nome da cidade consultada

    Retorna:
        dict com os dados meteorológicos retornados pela API
    """

    # endpoint da API de previsão do tempo
    url = "https://api.open-meteo.com/v1/forecast"

    # parâmetros enviados para a API
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,precipitation,wind_speed_10m",
        "timezone": "America/Sao_Paulo"
    }

    print(f"Consultando dados meteorológicos para {cidade}...")

    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Erro na API para {cidade}: {response.status_code}")

    data = response.json()

    # adiciona o nome da cidade ao JSON para facilitar a transformação depois
    data["city"] = cidade

    print(f"Dados extraídos com sucesso para {cidade}.")

    return data


if __name__ == "__main__":
    dados = extrair_dados_clima(
        latitude=-22.9068,
        longitude=-43.1729,
        cidade="Rio de Janeiro"
    )

    print(dados.keys())