import vertexai
from vertexai.generative_models import GenerativeModel
import os
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from PIL import Image
import requests
import re
import json
from st_aggrid import AgGrid, GridOptionsBuilder 
from datetime import datetime
from utils import verifica_iniciado, extrai_ds_resultado, extrai_ds_catcon, open_url_in_new_tab
from prompts import query_pre, query_template_ergo, query_template_cinti, query_template_angio
import webbrowser
import logging
import ricardio_secondpart
from detalhes_page import render_second_page

# Configuração para suprimir mensagens de warning
logging.getLogger('streamlit').setLevel(logging.ERROR)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ped-dev.json"
cred = service_account.Credentials.from_service_account_file('ped-dev.json')

# streamlit run dash.py
# env dashcardio python 3.10
# webbrowser

# gcloud auth revoke --all
# gcloud auth login
# gcloud config set project ped-dev-308120
# gcloud app deploy

# https://dash-cardio-dot-ped-dev-308120.rj.r.appspot.com/?email=aureliano.paiva@grupofleury.com.br	

# http://localhost:8501/?email=aureliano.paiva@grupofleury.com.br

if "show_second_page" not in st.session_state:
    st.session_state.show_second_page = False

if not st.session_state.show_second_page:
    st.set_page_config(
        page_title = "DASHBOARD RI CARDIO",
        page_icon = './CARDIO1.png',
        layout = 'wide',
        initial_sidebar_state = 'expanded',
        menu_items = {
            'About' : "Esse app foi desenvolvido para uso interno do grupo Fleury."
        }
    )

    query_painel = """ SELECT * FROM `ped-dev-308120.bdri.PD_CZTB_MEDICO_RI_MERI`; """
    df_medicos = pd.read_gbq(query_painel, project_id='ped-dev-308120', dialect='standard', credentials=cred)

    email = "aureliano.paiva@grupofleury.com.br"

    if ((df_medicos['MERI_DS_EMAIL'] == email) & (df_medicos['MEDI_IN_RI'] == True) & (df_medicos['MEDI_CD_GRUPO'] == 1)).any():
        mask = (df_medicos['MERI_DS_EMAIL'] == email) & (df_medicos['MEDI_IN_RI'] == True) & (df_medicos['MEDI_CD_GRUPO'] == 1)
        nome_medico = df_medicos.loc[mask, 'MEDI_NO_MEDICO'].values[0]
        cd_grupo_medico = df_medicos.loc[mask, 'MEDI_CD_GRUPO'].values[0]
        email_medico = df_medicos.loc[mask, 'MERI_DS_EMAIL'].values[0]
        tratamento = df_medicos.loc[mask, 'MEDI_SL_TITULO'].values[0]
        no_crm = df_medicos.loc[mask, 'MERI_NR_CERTIFICADO'].values[0]
        uf = df_medicos.loc[mask, 'MERI_DS_UF_ORIGEM_CERTIFICADO'].values[0]


        st.header(":bar_chart: RI CARDIO")
        st.write(f"Seja bem vindo, {tratamento} {nome_medico}!")

        query_painel = """ SELECT * FROM `ped-dev-308120.bdri.PD_CZVW_CLIENTE_RI_ELEGIVEL_CREL`; """
        df = pd.read_gbq(query_painel, project_id='ped-dev-308120', dialect='standard', credentials=cred)
        df = df[df['CREL_JO_CLIENTE'].notna()]
        # Aplique a função à coluna CREL_JO_CLIENTE para criar a coluna INICIADO
        df['INICIADO'] = df['CREL_JO_CLIENTE'].apply(verifica_iniciado)

        # Ajustando o tipo de dados nas colunas
        df['CREL_NR_CLIENTE'] = df['CREL_NR_CLIENTE'].astype(str)
        df['CREL_SL_MARCA'] = df['CREL_SL_MARCA'].astype(str)
        df['CREL_DT_NASCTO'] = df['CREL_DT_NASCTO'].astype(str)
        df['INICIADO'] = df['INICIADO'].astype(str)
        #df['RI_INICIADO'] = False

        df_json = df[["CREL_NR_CLIENTE", "CREL_JO_CLIENTE"]].copy()

        # Configurando a barra lateral
        with st.sidebar:
            # Colocando a logo
            logo_teste = Image.open('./logo.png')
            st.image(logo_teste, width=100)
            logo_teste = Image.open('./CARDIO1.png')
            st.image(logo_teste, width=200)
                        
            # Colocando o título da barra lateral
            st.subheader("MENU - RI CARDIO")

            # Criar uma caixa de seleção multiseleção
            # Filtros
            options1 = list(df['CREL_SL_MARCA'].unique()) + ['All']
            marca = st.multiselect("Selecione a Marca:", default='All', options = options1)
            if (marca == ['All']) | (marca == []):
                options2 = list(df['CREL_SL_MARCA'].unique()) 
            else:
                options2 = marca

            options3 = list(df['CREL_SL_REGIONAL'][df['CREL_SL_MARCA'].isin(options2)].unique()) + ['All']
            regional = st.multiselect("Selecione a Regional:", default='All', options = options3)

            if (regional == ['All']) | (regional == []):
                options3 = list(df['CREL_SL_REGIONAL'].unique()) 
            else:
                options3 = regional

            iniciado = list(df['INICIADO'].unique()) + ['All']
            iniciado_cond = st.multiselect("Status (Iniciado/Não)", default='All', options = iniciado)

            if (iniciado_cond == ['All']) | (iniciado_cond == []):
                iniciado2 = list(df['INICIADO'].unique()) 
            else:
                iniciado2 = iniciado_cond

            df = df.loc[(df["CREL_SL_MARCA"].isin(options2)) & (df['CREL_SL_REGIONAL'].isin(options3)) & (df['INICIADO'].isin(iniciado2))]

            # & (df['INICIADO'].isin(iniciado2))
                

        #####PÁGINA PRINCIPAL#####
        # Escrevendo o total de pacientes
        total_pacientes = round(df["CREL_NR_CLIENTE"].nunique(),2) 
        # Criando as colunas que vão dar espaçamento entre as destaques
        n1, n2, n3, n4, n5, n6 = st.columns(6) 
        with n1:
            st.write('**TOTAL DE PACIENTES:**')
            st.info(f"{total_pacientes}")

        # Trabalhando no df
        # # Renomeando as colunas do df
        df.rename(columns={'CREL_SL_MARCA': 'MARCA'}, inplace=True)
        df.rename(columns={'CREL_SL_REGIONAL': 'REGIONAL'}, inplace=True)
        df.rename(columns={'CREL_NR_CLIENTE': 'NR_PACIENTE'}, inplace=True)
        df.rename(columns={'CREL_NO_CLIENTE': 'NOME_PACIENTE'}, inplace=True)
        df.rename(columns={'CREL_DT_NASCTO': 'DT_NASCIMENTO'}, inplace=True)
        df.rename(columns={'CREL_SL_SEXO': 'SEXO'}, inplace=True)
        df.rename(columns={'CREL_NR_CPF': 'CPF'}, inplace=True)

        # Crie três novas colunas para cada DS_RESULTADO
        for i in range(3):
            df[f'DS_RESULTADO_{i+1}'] = df['CREL_JO_CLIENTE'].apply(lambda x: extrai_ds_resultado(x, i))
            df.rename(columns={'DS_RESULTADO_1': 'LAUDO_ERGO'}, inplace=True) 
            df.rename(columns={'DS_RESULTADO_2': 'LAUDO_CINTI'}, inplace=True)
            df.rename(columns={'DS_RESULTADO_3': 'LAUDO_ANGIO'}, inplace=True)
            
        # Crie três novas colunas para cada DS_CATCON
        for i in range(3):
            df[f'DS_CATCON_{i+1}'] = df['CREL_JO_CLIENTE'].apply(lambda x: extrai_ds_catcon(x, i))
            df.rename(columns={'DS_CATCON_1': 'RESULTADO_ERGO'}, inplace=True) 
            df.rename(columns={'DS_CATCON_2': 'RESULTADO_CINTI'}, inplace=True)
            df.rename(columns={'DS_CATCON_3': 'RESULTADO_ANGIO'}, inplace=True)

        teste = df['CREL_JO_CLIENTE']
        df['JSON'] = df['CREL_JO_CLIENTE']
        df = df.drop('CREL_JO_CLIENTE', axis=1) 
        df['CREL_JO_CLIENTE'] = df['JSON']
        df = df.drop('JSON', axis=1)

        # Configurando a apresentação da planilha no dashboard
        # Configure grid options using GridOptionsBuilder
        df = df.drop(['CREL_JO_CLIENTE'], axis=1)
        builder = GridOptionsBuilder.from_dataframe(df) 
        builder.configure_pagination(enabled=True, paginationAutoPageSize=False) 
        builder.configure_side_bar()
        builder.configure_selection(use_checkbox=True) 
        grid_options = builder.build()

        # Defina as larguras das colunas desejadas em pixels
        col_widths = {'MARCA': 5, 'REGIONAL': 5, 'CPF': 10,'NR_PACIENTE': 10, 'NOME_PACIENTE': 100, 'DT_NASCIMENTO':10,'SEXO': 5, 'RI_INICIADO': 5 }

        # Definindo a largura e altura da tabela
        largura_tabela = 5  # Em pixels
        altura_tabela = 400  # Em pixels

        
        # Display AgGrid
        st.write("Selecione um paciente para fazer o Relatório Integrado")
        return_value = AgGrid(df, 
                            gridOptions=grid_options,  
                            config={'columnWidths': col_widths},
                            reload_data = True,
                                allow_unsafe_jscode = True,
                                fit_columns_on_grid_load = False,
                                enable_enterprise_modules = False,
                                height = 320,
                                width = '100%',
                                theme = "streamlit"
                                )

        # Retorna o json após o usuário selecionar um paciente
        # extracted_dict = json.loads(string_with_dict)
        
        try:
            selecao = return_value['selected_rows']
            nrpaciente_filter = selecao['NR_PACIENTE'][0]
        
            extracted_dict = json.loads(df_json['CREL_JO_CLIENTE'][df_json['CREL_NR_CLIENTE'] == nrpaciente_filter].values[0])

            LAU_ERGOMETRIA = (selecao['LAUDO_ERGO'][0])
            LAU_CINTILOGRAFIA = (selecao['LAUDO_CINTI'][0])
            LAU_ANGIOTOMOGRAFIA = (selecao['LAUDO_ANGIO'][0])
                            
            # Tratando o texto do laudo de ERGOMETRIA
            divisores_ergo_1 = r'Conclusões|CONCLUSÃO DO EXAME:|COMENTÁRIO:|COMENTÁRIOS:|Conclusão:|Conclusão|CONCLUSÃO|Considerações finais|INTERPRETAÇÃO FINAL|Respostas  clínica,  cronotrópica,  inotrópica,  autonômica  e  eletrocardiográfica  adequadas  ao  esforço  realizado.|Avaliação final|Avaliação Final|Redução da frequência cardíaca, no primeiro minuto da fase de recuperação, dentro dos valores esperados.|Ausência  de  alterações  do  ritmo,  da  condução  ou  da  repolarização ventricular  diagnósticas  de  isquemia miocárdica nas fases de esforço e de recuperação.|Redução da frequência cardíaca, no primeiro minuto da fase de recuperação, abaixo dos valores esperados.|Redução da frequência cardíaca, no primeiro minuto da fase de recuperação, abaixo  dos valores esperados.'
            laudo_ergo_1 = re.split(divisores_ergo_1, LAU_ERGOMETRIA)[1]
            divisores_ergo_2 = r'Obs: Laudo|Valores de referência:|Classificação dos graus de estenose:|Laudo elaborado de acordo com a III Diretrizes da Sociedade Brasileira de Cardiologia sobre Teste Ergométrico.|Laudado por:'
            laudo_ergo_2 = re.split(divisores_ergo_2, laudo_ergo_1)[0]
            divisores_ergo_3 = r'Obs: Laudo|Valores de referência:|Classificação dos graus de estenose:|III Diretrizes da Sociedade Brasileira de Cardiologia sobre Teste Ergométrico.|Laudado por:'
            laudo_ergo = re.split(divisores_ergo_3, laudo_ergo_2)[0]

            # Tirando os espaços em branco desnecessários
            s = laudo_ergo
            laudo_ergo_t = re.sub(' {2,}', ' ', s).strip(' ')
                        
            # Tratando o texto do laudo de CINTILOGRAFIA
            divisores_cinti_1 = r'COMENTÁRIOS:|COMENTÁRIOS|Impressão Diagnóstica:|IMPRESSÃO DIAGNÓSTICA:|Conclusão:|Conclusões:|Conclusão|OBSERVAÇÕES|Impressão:|IMPRESSÃO|Impressão'
            laudo_cinti_1 = re.split(divisores_cinti_1, LAU_CINTILOGRAFIA)[1]
            divisores_cinti_2 = r'Obs: Laudo|Valores de referência:|Classificação dos graus de estenose:|Laudo elaborado de acordo com a III Diretrizes da Sociedade Brasileira de Cardiologia sobre Teste Ergométrico.|Laudado por:'
            laudo_cinti_2 = re.split(divisores_cinti_2, laudo_cinti_1)[0]
            divisores_cinti_3 = r'Obs: Laudo|Valores de referência:|Classificação dos graus de estenose:|III Diretrizes da Sociedade Brasileira de Cardiologia sobre Teste Ergométrico.|Laudado por:'
            laudo_cinti = re.split(divisores_cinti_3, laudo_cinti_2)[0]

            # Tirando os espaços em branco desnecessários
            s = laudo_cinti
            laudo_cinti_t = re.sub(' {2,}', ' ', s).strip(' ')

            # Tratando o texto do laudo de ANGIOTOMOGRAFIA
            divisores_angio_1 = r'Observação: |Comentários|IMPRESSÃO DIAGNÓSTICA:|IMPRESSÃO|CONCLUSÕES|Impressão diagnóstica:|Impressão diagnóstica:|Coronária  direita  dominante  com|Impressão Diagnóstica:|Ramos diagonais pérvios.  Artéria circunflexa atinge o terço distal do sulco AV esquerdo, sem lesões obstrutivas. Ramos marginais pérvios.'
            laudo_angio_1 = re.split(divisores_angio_1, LAU_ANGIOTOMOGRAFIA)[1]
            divisores_angio_2 = r'Obs: Laudo|Valores de referência:|Classificação dos graus de estenose:|Laudo elaborado de acordo com a III Diretrizes da Sociedade Brasileira de Cardiologia sobre Teste Ergométrico.|Laudado por:'
            laudo_angio_2 = re.split(divisores_angio_2, laudo_angio_1)[0]
            divisores_angio_3 = r'Obs: Laudo|Valores de referência:|Classificação dos graus de estenose:|III Diretrizes da Sociedade Brasileira de Cardiologia sobre Teste Ergométrico.|Laudado por:'
            laudo_angio = re.split(divisores_angio_3, laudo_angio_2)[0]

            # Tirando os espaços em branco desnecessários
            s = laudo_angio
            laudo_angio_t = re.sub(' {2,}', ' ', s).strip(' ')

            # VERTEX
            vertexai.init(project='ped-dev-308120', location="us-central1", credentials=cred)
            parameters = {"temperature": 0.0, "top_p": 0.2, "top_k": 1}
            model = GenerativeModel("gemini-2.0-flash")

            
            texto_ergo = laudo_ergo_t
            query = query_pre  + f'{texto_ergo}' + query_template_ergo
            res_ergo = model.generate_content(query, generation_config=parameters)
            res_ergo = res_ergo.text
            res_ergo = res_ergo.replace(".", "")

            texto_cinti = laudo_cinti_t
            query = query_pre  + f'{texto_cinti}' + query_template_cinti
            res_cinti = model.generate_content(query, generation_config=parameters)
            res_cinti = res_cinti.text
            res_cinti = res_cinti.replace(".", "")

            texto_angio = laudo_angio_t
            query = query_pre  + f'{texto_angio}' + query_template_angio
            res_angio = model.generate_content(query, generation_config=parameters)
            res_angio = res_angio.text

            ############################# Construindo o dicionário #################################
            data_dict = {"SL_MARCA": selecao['MARCA'][0],
                        "SL_REGIONAL": selecao['REGIONAL'][0],
                        "NR_CPF": selecao['CPF'][0],
                        "NR_CLIENTE": selecao['NR_PACIENTE'][0],
                        "NO_CLIENTE": selecao['NOME_PACIENTE'][0],
                        "DT_NASCTO": selecao['DT_NASCIMENTO'][0],
                        "SL_SEXO": selecao['SEXO'][0],
                        "MEDICO_RI": nome_medico,
                        "GRUPO_MEDICO_RI": str(cd_grupo_medico),
                        "EMAIL_MEDICO_RI": email_medico,
                        "tratamento": tratamento,
                        "CRM": no_crm,
                        "UF_CRM": uf,
                        "exames":[
                                {# ERGOMETRIA
                                "DH_ATENDIMENTO": extracted_dict['exames'][0]['DH_ATENDIMENTO'],
                                    "NR_FICHA": extracted_dict['exames'][0]['NR_FICHA'],
                                    "SL_CATEGORIA": extracted_dict['exames'][0]['SL_CATEGORIA'],
                                    "NR_CERTIFICADO": extracted_dict['exames'][0]['NR_CERTIFICADO'],
                                    "DS_UF_CERT": extracted_dict['exames'][0]['DS_UF_CERT'],
                                    "NR_TELEFONE_MEDICO": extracted_dict['exames'][0]['NR_TELEFONE_MEDICO'],
                                    "DS_EMAIL_MEDICO": extracted_dict['exames'][0]['DS_EMAIL_MEDICO'],
                                    "NR_ACESSION_NUMBER": extracted_dict['exames'][0]['NR_ACESSION_NUMBER'],
                                    "NO_SUBGRUPO": extracted_dict['exames'][0]['NO_SUBGRUPO'], 
                                    "SL_EXAME": extracted_dict['exames'][0]['SL_EXAME'],
                                    "DS_RESULTADO": extracted_dict['exames'][0]['DS_RESULTADO'],
                                    "DS_CONCLUSAO_IA": res_ergo,
                                    "DS_CATCON": extracted_dict['exames'][0]['DS_CATCON']},
                                {# CINTILOGRAFIA
                                    "DH_ATENDIMENTO": extracted_dict['exames'][1]['DH_ATENDIMENTO'],
                                    "NR_FICHA": extracted_dict['exames'][1]['NR_FICHA'],
                                    "SL_CATEGORIA": extracted_dict['exames'][1]['SL_CATEGORIA'],
                                    "NR_CERTIFICADO": extracted_dict['exames'][1]['NR_CERTIFICADO'],
                                    "DS_UF_CERT": extracted_dict['exames'][1]['DS_UF_CERT'],
                                    "NR_TELEFONE_MEDICO": extracted_dict['exames'][1]['NR_TELEFONE_MEDICO'],
                                    "DS_EMAIL_MEDICO": extracted_dict['exames'][1]['DS_EMAIL_MEDICO'],
                                    "NR_ACESSION_NUMBER": extracted_dict['exames'][1]['NR_ACESSION_NUMBER'],
                                    "NO_SUBGRUPO": extracted_dict['exames'][1]['NO_SUBGRUPO'],
                                    "SL_EXAME": extracted_dict['exames'][1]['SL_EXAME'],
                                    "DS_RESULTADO": extracted_dict['exames'][1]['DS_RESULTADO'],
                                    "DS_CONCLUSAO_IA": res_cinti,
                                    "DS_CATCON": extracted_dict['exames'][1]['DS_CATCON']},
                                {# ANGIOTOMOGRAFIA
                                    "DH_ATENDIMENTO": extracted_dict['exames'][2]['DH_ATENDIMENTO'],
                                    "NR_FICHA": extracted_dict['exames'][2]['NR_FICHA'],
                                    "SL_CATEGORIA": extracted_dict['exames'][2]['SL_CATEGORIA'],
                                    "NR_CERTIFICADO": extracted_dict['exames'][2]['NR_CERTIFICADO'],
                                    "DS_UF_CERT": extracted_dict['exames'][2]['DS_UF_CERT'],
                                    "NR_TELEFONE_MEDICO": extracted_dict['exames'][2]['NR_TELEFONE_MEDICO'],
                                    "DS_EMAIL_MEDICO": extracted_dict['exames'][2]['DS_EMAIL_MEDICO'],
                                    "NR_ACESSION_NUMBER": extracted_dict['exames'][2]['NR_ACESSION_NUMBER'],
                                    "NO_SUBGRUPO": extracted_dict['exames'][2]['NO_SUBGRUPO'],
                                    "SL_EXAME": extracted_dict['exames'][2]['SL_EXAME'],
                                    "DS_RESULTADO": extracted_dict['exames'][2]['DS_RESULTADO'],
                                    "DS_CONCLUSAO_IA": res_angio,
                                    "DS_CATCON": extracted_dict['exames'][2]['DS_CATCON']}]}
            
            url_ri = 'https://ri-cardio-dot-ped-dev-308120.rj.r.appspot.com'

            with n1:
                st.write('SELEÇÃO')
                #ricardio_secondpart.render(data_dict)
                #render_second_page()
                st.session_state.show_second_page = True
                st.session_state.show_second_page = data_dict
                st.rerun()

        except Exception as e:
            #st.write('')
            print(f"Error:{e}")

    else:
        st.header(":bar_chart: RI CARDIO")
        st.write(f"Você não tem acesso ao RI CARDIO. Entre em contato com o GCDB.")
        st.write(f"Email: gcdb@grupofleury.com.br")

else:
    ricardio_secondpart.render(st.session_state.show_second_page)
