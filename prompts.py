query_pre = """ em português, dado o texto:"""

query_template_ergo = """
    Classifique entre:
    "Normal" ou "Isquêmico" ou "Inconclusivo"
    traga apenas a classificação, sem nenhum texto adicional
    """

query_template_cinti = """
    Classifique entre:
    "Normal" ou "Isquêmico" ou "Fibrose" ou "Fibrose com isquemia"
    traga apenas a classificação, sem nenhum texto adicional
    """

query_template_angio = """
    Deve trazer apenas uma das classificações e usar a seguinte ordem de prioridade:
    primeiro: verificar se é oclusão , se for, classificar como "Oclusão";
    se não for, segundo: verificar se é placas significativas, se for, classificar como "Placas significativas";
    se também não for, terceiro: verificar se é placas moderadas nas artérias coronárias, se for, classificar como "Placas moderadas nas artérias coronárias";
    se também não for, quarto: verificar se é placas discretas nas artérias coronárias, se for, classificar como "Placas discretas nas artérias coronárias";
    se também não for, quinto: verificar se é ausência de placas obstrutivas, com sinais de placas de ateroma discretas não calcificadas, se for, classificar como "Ausência de placas obstrutivas, com sinais de placas de ateroma discretas não calcificadas";
    se também não for, sexto: verificar se é ausência de placas e obstruções coronárias, se for, classificar como "Ausência de placas e obstruções coronárias".

    exemplo:
    se tiver no texto "discreta / moderada" classifique como "Placas moderadas nas artérias coronárias"
    se tiver no texto "discreta/moderada" classifique como "Placas moderadas nas artérias coronárias"
    se tiver no texto "discreta / moderada" classifique como "Placas moderadas nas artérias coronárias"
    se tiver no texto "Estenose moderada" classifique como "Placas moderadas nas artérias coronárias"
    se tiver no texto "Placas de ateroma de discretas a moderadas" classifique como "Placas moderadas nas artérias coronárias"
    se tiver no texto "Placas de ateroma de discreta a discreta / moderada" classifique como "Placas moderadas nas artérias coronárias"
    se tiver no texto "Placas de ateroma de discreta a discreta/moderada" classifique como "Placas moderadas nas artérias coronárias"

    se tiver no texto "aterosclerose difusa" classifique como "Placas significativas"
    se tiver no texto "moderado/significativo" classifique como "Placas significativas"
    se tiver no texto "discreto a moderado/significativo" classifique como "Placas significativas"
    se tiver no texto "Placas de ateroma nas artérias coronárias de grau discreto a moderado/significativo" classifique como "Placas significativas"

    traga apenas a classificação, sem nenhum texto adicional
    
    """