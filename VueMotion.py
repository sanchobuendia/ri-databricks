import requests
import json


def request_api(ficha: str, item: str):
    """Esta função faz a requisição da API do VueMotion e retorna o link da imagem do exame.
    param ficha: Número da ficha do exame.
    param item: Número do item do exame.
    """

    url = "https://api.grupofleury.com.br/oauth/grant-code"

    payload = json.dumps(
        {
            "client_id": "89225440-0873-3bb6-9c79-e0331ea646a7",
            "redirect_uri": "http://localhost",
        }
    )
    headers = {"Content-Type": "application/json"}

    code = requests.request("POST", url, headers=headers, data=payload)
    code = code.json()
    code = code["redirect_uri"].split("code=")[1]

    url = "https://api.grupofleury.com.br/oauth/access-token"
    payload = "grant_type=authorization_code&code=" + code
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "client_id": "89225440-0873-3bb6-9c79-e0331ea646a7",
        "Authorization": "Basic ODkyMjU0NDAtMDg3My0zYmI2LTljNzktZTAzMzFlYTY0NmE3OjM4YjU1NDlkLTZlMDgtM2YxNC04OWY3LTNlZjE1M2I4MmRkNg==",
    }

    access_token = requests.request("POST", url, headers=headers, data=payload)
    access_token = access_token.json()
    access_token = access_token["access_token"]

    url = (
        "https://api.grupofleury.com.br/resultado-de-exames/v2/fichas/"
        + str(ficha)
        + "/itens/"
        + str(item)
        + "/imagens"
    )
    payload = {}
    headers = {
        "client_id": "89225440-0873-3bb6-9c79-e0331ea646a7",
        "access_token": access_token,
    }
    link = requests.request("GET", url, headers=headers, data=payload)
    link = link.json()
    link = link["urlImage"]

    return link
