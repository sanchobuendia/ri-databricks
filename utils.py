import json

# Verifica se o RI foi iniciado
# Defina uma função para verificar se o campo DS_CATCON está vazio ou não
def verifica_iniciado(json_str):
    try:
        data = json.loads(json_str)
        exames = data.get("exames", [])
        for exame in exames:
            if exame.get("DS_CATCON"):
                return "SIM"
        return "NÃO"
    except (json.JSONDecodeError, AttributeError):
        return "ERRO"
    
# Extrai o DS_RESULTADO de cada exame
# Defina uma função para extrair os valores de DS_CATCON
def extrai_ds_resultado(json_str, indice):
    try:
        data = json.loads(json_str)
        exames = data.get("exames", [])
        if len(exames) > indice:
            return exames[indice].get("DS_RESULTADO", "NÃO")
        else:
            return "NÃO"
    except (json.JSONDecodeError, AttributeError, IndexError):
        return "erro"
    
# Extrai o DS_CATCON de cada exame
# Defina uma função para extrair os valores de DS_CATCON
def extrai_ds_catcon(json_str, indice):
    try:
        data = json.loads(json_str)
        exames = data.get("exames", [])
        if len(exames) > indice:
            return exames[indice].get("DS_CATCON", "NÃO")
        else:
            return "NÃO"
    except (json.JSONDecodeError, AttributeError, IndexError):
        return "erro"
    
def open_url_in_new_tab(url):
    webbrowser.open_new_tab(url)




    
