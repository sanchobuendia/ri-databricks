import streamlit as st
import os
import pandas as pd
from VueMotion import request_api
from utils_secondpart import finish_ri, update_exames
from utils_API import (
    create_ri,
    calculate_age,
    show_pdf,
    conclusao_integrada
)
from google.oauth2 import service_account
from google.cloud import storage, bigquery
import streamlit_authenticator as stauth
import numpy as np
import requests
import json
import datetime
from datetime import datetime
import re
from PIL import Image
import shutil
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import PIL
import yaml
from yaml.loader import SafeLoader

import logging

# Configuração para suprimir mensagens de warning
logging.getLogger('streamlit').setLevel(logging.ERROR)

import warnings
warnings.filterwarnings("ignore")


# conda create -n ricardio python=3.9
# conda activate ricardio
# pip install --upgrade pip
# pip install --upgrade setuptools wheel
# pip install -r requirements.txt
# streamlit run RI.py

# gcloud auth revoke --all
# gcloud auth login
# gcloud config set project ped-dev-308120
# gcloud app deploy

#   http://localhost:8501/?email=aureliano.paiva@grupofleury.com.br

def render(data_dict):

    CLRI_NR_CLIENTE = data_dict['NR_CLIENTE']
    MEDICO = data_dict['MEDICO_RI']
    CLRI_SL_MARCA = data_dict['SL_MARCA']
    CLRI_SL_REGIONAL = data_dict['SL_REGIONAL']
    CLRI_NO_CLIENTE = data_dict['NO_CLIENTE']
    CLRI_DT_NASCTO = data_dict['DT_NASCTO']
    CLRI_SL_SEXO = data_dict['SL_SEXO']
    NR_CPF = data_dict['NR_CPF']
    tratamento = data_dict['tratamento']
    CRM = data_dict['CRM']
    UF_CRM = data_dict['UF_CRM']

    ERGOMETRIA_CLRI_SL_EXAME = data_dict["exames"][0]['SL_EXAME']
    ERGOMETRIA_Laudo = data_dict["exames"][0]['DS_RESULTADO'].strip()
    ERGOMETRIA_CONCLUSAO_INDIV = data_dict["exames"][0]['DS_CONCLUSAO_IA']
    ERGOMETRIA_CLRI_NR_ACESSION_NUMBER = data_dict["exames"][0]['NR_ACESSION_NUMBER']
    ERGOMETRIA_FICHA = data_dict["exames"][0]['NR_FICHA']
    ERGOMETRIA_SL_CATEGORIA = data_dict["exames"][0]['SL_CATEGORIA']
    ERGOMETRIA_NR_CERTIFICADO = data_dict["exames"][0]['NR_CERTIFICADO']
    ERGOMETRIA_DS_UF_CERT = data_dict["exames"][0]['DS_UF_CERT']
    ERGOMETRIA_NR_TELEFONE_MEDICO = data_dict["exames"][0]['NR_TELEFONE_MEDICO']
    ERGOMETRIA_DS_EMAIL_MEDICO = data_dict["exames"][0]['DS_EMAIL_MEDICO']
    ERGOMETRIA_NO_SUBGRUPO = data_dict["exames"][0]['NO_SUBGRUPO']

    CINTILOGRAFIA_CLRI_SL_EXAME = data_dict["exames"][1]['SL_EXAME']
    CINTILOGRAFIA_Laudo = data_dict["exames"][1]['DS_RESULTADO'].strip()
    CINTILOGRAFIA_CONCLUSAO_INDIV = data_dict["exames"][1]['DS_CONCLUSAO_IA']
    CINTILOGRAFIA_CLRI_NR_ACESSION_NUMBER = data_dict["exames"][1]['NR_ACESSION_NUMBER']
    CINTILOGRAFIA_FICHA = data_dict["exames"][1]['NR_FICHA']
    CINTILOGRAFIA_SL_CATEGORIA = data_dict["exames"][1]['SL_CATEGORIA']
    CINTILOGRAFIA_NR_CERTIFICADO = data_dict["exames"][1]['NR_CERTIFICADO']
    CINTILOGRAFIA_DS_UF_CERT = data_dict["exames"][1]['DS_UF_CERT']
    CINTILOGRAFIA_NR_TELEFONE_MEDICO = data_dict["exames"][1]['NR_TELEFONE_MEDICO']
    CINTILOGRAFIA_DS_EMAIL_MEDICO = data_dict["exames"][1]['DS_EMAIL_MEDICO']
    CINTILOGRAFIA_NO_SUBGRUPO = data_dict["exames"][1]['NO_SUBGRUPO']

    ANGIOTOMOGRAFIA_CLRI_SL_EXAME = data_dict["exames"][2]['SL_EXAME']
    ANGIOTOMOGRAFIA_Laudo = data_dict["exames"][2]['DS_RESULTADO'].strip()
    ANGIOTOMOGRAFIA_CONCLUSAO_INDIV = data_dict["exames"][2]['DS_CONCLUSAO_IA']
    ANGIOTOMOGRAFIA_CLRI_NR_ACESSION_NUMBER = data_dict["exames"][2]['NR_ACESSION_NUMBER']
    ANGIOTOMOGRAFIA_FICHA = data_dict["exames"][2]['NR_FICHA']
    ANGIOTOMOGRAFIA_SL_CATEGORIA = data_dict["exames"][2]['SL_CATEGORIA']
    ANGIOTOMOGRAFIA_NR_CERTIFICADO = data_dict["exames"][2]['NR_CERTIFICADO']
    ANGIOTOMOGRAFIA_DS_UF_CERT = data_dict["exames"][2]['DS_UF_CERT']
    ANGIOTOMOGRAFIA_NR_TELEFONE_MEDICO = data_dict["exames"][2]['NR_TELEFONE_MEDICO']
    ANGIOTOMOGRAFIA_DS_EMAIL_MEDICO = data_dict["exames"][2]['DS_EMAIL_MEDICO']
    ANGIOTOMOGRAFIA_NO_SUBGRUPO = data_dict["exames"][2]['NO_SUBGRUPO']

    ITEM_ERGOMETRIA = ERGOMETRIA_CLRI_NR_ACESSION_NUMBER[13::]
    ITEM_CINTILOGRAFIA = CINTILOGRAFIA_CLRI_NR_ACESSION_NUMBER[13::]
    ITEM_ANGIOTOMOGRAFIA = ANGIOTOMOGRAFIA_CLRI_NR_ACESSION_NUMBER[13::]

    dict_changes = {
        "CLRI_NR_CLIENTE": "CLRI_NR_CLIENTE",
        "imagens_Ergometria": False,
        "imagens_Cintilografia": False,
        "imagens_Angiotomografia": False,
        "classificacao_Ergometria": None,
        "classificacao_Cintilografia": None,
        "classificacao_Angiotomografia": None,
        "conclusao_integrada": None,
    }

    if 'user_logs' not in st.session_state:
        st.session_state.user_logs = dict_changes
        
    credentials = service_account.Credentials.from_service_account_file('ped-dev.json')
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket("ped-dev-dados")

    client = bigquery.Client(credentials= credentials)
    datatoday = datetime.now()
    datatoday = datatoday.strftime("%Y-%m-%d %H:%M:%S")


    blobs_ergofiles = storage_client.list_blobs(bucket_or_name="ped-dev-dados", prefix=f"ri-cardio/clientes/{CLRI_NR_CLIENTE}/ergometria/")
    ergofiles = sum(1 for _ in blobs_ergofiles)
        
    blobs_cintfiles = storage_client.list_blobs(bucket_or_name="ped-dev-dados", prefix=f"ri-cardio/clientes/{CLRI_NR_CLIENTE}/cintilografia/")
    cintfiles = sum(1 for _ in blobs_cintfiles)

    blobs_angiofiles = storage_client.list_blobs(bucket_or_name="ped-dev-dados", prefix=f"ri-cardio/clientes/{CLRI_NR_CLIENTE}/angiotomografia/")
    angiofiles = sum(1 for _ in blobs_angiofiles)

    css = """<style>section.main > div {max-width:75rem}</style>"""
    st.markdown(css, unsafe_allow_html=True)

    st.empty()

    st.write(f"Seja bem vindo, {tratamento} {MEDICO}!")

    st.title("RI de cardio")

    coll1, coll2, col3 = st.columns(3)
    with coll1:
        marca = st.selectbox("Marca", [CLRI_SL_MARCA])  # 427

    with coll2:
        regional = st.selectbox("Regional", [CLRI_SL_REGIONAL])

    with col3:
        option_cliente = st.selectbox("ID do cliente", [CLRI_NR_CLIENTE])  # 427

    col5, col6, col7 = st.columns(3)

    with col5:
        with st.form("Ergometria", clear_on_submit=True): 
            uploaded_files = st.file_uploader(
                f"Ergometria. Ficha = {ERGOMETRIA_FICHA}. Exame = {ERGOMETRIA_CLRI_SL_EXAME}",
                accept_multiple_files=True,
                type=["png", "jpg", "jpeg"],
            )

            n1, n2, n3 = st.columns(3)
            with n1:
                v1 = st.form_submit_button("VueMotion")
                if v1:
                    optf = ERGOMETRIA_FICHA
                    opti = ITEM_ERGOMETRIA
                    link = request_api(optf, opti)
                    st.markdown(link, unsafe_allow_html=False)

            with n2:
                refazer_ergo = st.form_submit_button("Refazer")
                if refazer_ergo:
                    blobs_ergofiles = storage_client.list_blobs(bucket_or_name="ped-dev-dados", prefix=f"ri-cardio/clientes/{CLRI_NR_CLIENTE}/ergometria/")
                    for blob in blobs_ergofiles:
                        blob.delete()

            with n3:
                submitted1 = st.form_submit_button("Save")
                folder_blob = bucket.blob(
                    f"ri-cardio/clientes/{CLRI_NR_CLIENTE}" + "/ergometria/"
                )
                folder_blob.upload_from_string("")
                if submitted1:
                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            filename, ext = os.path.splitext(uploaded_file.name)
                            blob = bucket.blob(
                                f"ri-cardio/clientes/{CLRI_NR_CLIENTE}/ergometria/{filename}.png"
                            )
                            blob.upload_from_file(uploaded_file)
                            st.session_state.user_logs["imagens_Ergometria"] = True
                            st.success("Arquivo salvo na pasta!")

    with col6:
        with st.form("Cintilografia", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                f"Cintilografia. Ficha = {CINTILOGRAFIA_FICHA}. Exame = {CINTILOGRAFIA_CLRI_SL_EXAME}",
                accept_multiple_files=True,
                type=["png", "jpg", "jpeg"],
            )

            n4, n5, n6 = st.columns(3)
            with n4:
                v1 = st.form_submit_button("VueMotion")
                if v1:
                    optf = CINTILOGRAFIA_FICHA
                    opti = ITEM_CINTILOGRAFIA
                    link = request_api(optf, opti)
                    st.markdown(link, unsafe_allow_html=False)

            with n5:
                refazer_cinti = st.form_submit_button("Refazer")
                if refazer_cinti:
                    blobs_cintfiles = storage_client.list_blobs(bucket_or_name="ped-dev-dados", prefix=f"ri-cardio/clientes/{CLRI_NR_CLIENTE}/cintilografia/")
                    for blob in blobs_cintfiles:
                        blob.delete()

            with n6:
                submitted2 = st.form_submit_button("Save")
                folder_blob = bucket.blob(
                    f"ri-cardio/clientes/{CLRI_NR_CLIENTE}" + "/cintilografia/"
                )
                folder_blob.upload_from_string("")
                if submitted2:
                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            filename, ext = os.path.splitext(uploaded_file.name)
                            blob = bucket.blob(
                                f"ri-cardio/clientes/{CLRI_NR_CLIENTE}/cintilografia/{filename}.png"
                            )
                            blob.upload_from_file(uploaded_file)
                            st.session_state.user_logs["imagens_Cintilografia"] = True
                            st.success("Arquivo salvo na pasta!")
    with col7:
        with st.form("Angiotomografia", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                f"Angiotomografia. Ficha = {ANGIOTOMOGRAFIA_FICHA}. \n Exame = {ANGIOTOMOGRAFIA_CLRI_SL_EXAME}",
                accept_multiple_files=True,
                type=["png", "jpg", "jpeg"],
            )

            n7, n8, n9 = st.columns(3)
            with n7:
                v1 = st.form_submit_button("VueMotion")
                if v1:
                    optf = ANGIOTOMOGRAFIA_FICHA
                    opti = ITEM_ANGIOTOMOGRAFIA
                    link = request_api(optf, opti)
                    st.markdown(link, unsafe_allow_html=False)
            
            with n8:
                refazer_angio = st.form_submit_button("Refazer")
                if refazer_angio:
                    blobs_angiofiles = storage_client.list_blobs(bucket_or_name="ped-dev-dados", prefix=f"ri-cardio/clientes/{CLRI_NR_CLIENTE}/angiotomografia/")
                    for blob in blobs_angiofiles:
                        blob.delete()

            with n9:
                submitted3 = st.form_submit_button("Save")
                folder_blob = bucket.blob(f"ri-cardio/clientes/{CLRI_NR_CLIENTE}" + "/angiotomografia/")
                folder_blob.upload_from_string("")
                if submitted3:
                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            filename, ext = os.path.splitext(uploaded_file.name)
                            blob = bucket.blob(
                                f"ri-cardio/clientes/{CLRI_NR_CLIENTE}/angiotomografia/{filename}.png"
                            )
                            blob.upload_from_file(uploaded_file)
                            st.session_state.user_logs["imagens_Angiotomografia"] = True
                            st.success("Arquivo salvo na pasta!")

    if len(data_dict["exames"][0]['DS_CATCON']) > 1:
        ergoclass = data_dict["exames"][1]['DS_CATCON']
    else:
        ergoclass = ERGOMETRIA_CONCLUSAO_INDIV

    if len(data_dict["exames"][1]['DS_CATCON']) > 1:
        cintclass = data_dict["exames"][1]['DS_CATCON']
    else:
        cintclass = CINTILOGRAFIA_CONCLUSAO_INDIV

    if len(data_dict["exames"][2]['DS_CATCON']) > 1:
        angioclass = data_dict["exames"][1]['DS_CATCON']
    else:
        angioclass = ANGIOTOMOGRAFIA_CONCLUSAO_INDIV

    # angi0_res = f"Angiotomografia = {angioclass}"
    # erogo_res = f"Ergometria = {ergoclass}"
    # cint_res = f"Cintilografia = {cintclass}"

    # st.markdown(angi0_res)
    # st.markdown(erogo_res)
    # st.markdown(cint_res)

    res_data = {
        'Área': ['Angiotomografia', 'Ergometria', 'Cintilografia'],
        'Conclusão do Laudo': [ANGIOTOMOGRAFIA_Laudo, ERGOMETRIA_Laudo, CINTILOGRAFIA_Laudo],
        'Classificaçao': [angioclass, ergoclass, cintclass],
    }

    st.markdown("<h2>Classificação</h2>", unsafe_allow_html=True)

    res = pd.DataFrame(res_data)

    res["Classificaçao"] = res["Classificaçao"].str.strip()


    change = st.data_editor(
        res,
        width=2000, 
        hide_index=True,
        column_config={
            "Classificaçao": st.column_config.SelectboxColumn(
                "Classificaçao",
                help="The category of the app",
                options=['Ausência de placas e obstruções coronárias',
                        'Ausência de placas obstrutivas, com sinais de placas de ateroma discretas, não calcificadas',
                        'Placas discretas nas artérias coronárias',
                        'Placas moderadas nas artérias coronárias',
                        'Placas significativas',
                        'Oclusão',
                        'Normal', 
                        'Isquêmico',
                        'Inconclusivo',
                        'Fibrose', 'Fibrose com isquemia',
                ],
                required=True,
            )
        },
        
    )

    blob = bucket.blob("ri-cardio/build-classification/Conclusao_Integrada.xlsx")
    data_bytes = blob.download_as_bytes()
    regras_conclusao_integrada = pd.read_excel(data_bytes, sheet_name="Arvore de Decisao")
    regras_conclusao_integrada["ERGOMETRIA"] = regras_conclusao_integrada["ERGOMETRIA"].str.replace('\n', '')

    ci = conclusao_integrada(classes=list(change.Classificaçao), regras_conclusao_integrada=regras_conclusao_integrada)

    ci_origin = ci

    st.markdown("<h2>Conclusão Integrada</h2>", unsafe_allow_html=True)
    if ci == None:
        ci = "Favor escrever uma conclusão final!"
        ci = st.text_area(" ", ci)
    else:
        ci = st.text_area(" ", ci)

    if ci != ci_origin:
        st.session_state.user_logs["conclusao_integrada"] = ci
    else:
        pass

    blobs_ergofiles = storage_client.list_blobs(bucket_or_name="ped-dev-dados", prefix=f"ri-cardio/clientes/{CLRI_NR_CLIENTE}/ergometria/")
    ergofiles = sum(1 for _ in blobs_ergofiles)
        
    blobs_cintfiles = storage_client.list_blobs(bucket_or_name="ped-dev-dados", prefix=f"ri-cardio/clientes/{CLRI_NR_CLIENTE}/cintilografia/")
    cintfiles = sum(1 for _ in blobs_cintfiles)

    blobs_angiofiles = storage_client.list_blobs(bucket_or_name="ped-dev-dados", prefix=f"ri-cardio/clientes/{CLRI_NR_CLIENTE}/angiotomografia/")
    angiofiles = sum(1 for _ in blobs_angiofiles)

    if ergofiles > 1:
        finalergo = True
    else:
        finalergo = False

    if cintfiles > 1:
        finalcint = True
    else:
        finalcint = False

    if angiofiles > 1:
        finalangio = True
    else:
        finalangio = False

    if (finalergo is True) and (finalcint is True) and (finalangio is True):
        st.warning("Se todas as alterações no relatório integrado estiverem completas, clique em 'Finalizar RI'.")
        if st.button("Finalizar RI"):
            nome_medico = MEDICO
            option_ficha = ERGOMETRIA_FICHA
            cliente = CLRI_NR_CLIENTE
            sexo = CLRI_SL_SEXO
            birthdate = CLRI_DT_NASCTO
            idade = calculate_age(birthdate)
            output_pdf_path = create_ri(
                option_ficha, nome_medico, option_cliente, cliente, sexo, idade, ci
            )

            blob = bucket.blob(f"ri-cardio/relatorio-integrado-pdf/{output_pdf_path}")
            blob.upload_from_filename(output_pdf_path)

            show_pdf(output_pdf_path)

            if st.session_state.user_logs["classificacao_Ergometria"] != None:
                fergo = st.session_state.user_logs["classificacao_Ergometria"]
            else:
                fergo = ERGOMETRIA_CONCLUSAO_INDIV

            if st.session_state.user_logs["classificacao_Cintilografia"] != None:
                fcint = st.session_state.user_logs["classificacao_Cintilografia"]
            else:
                fcint = CINTILOGRAFIA_CONCLUSAO_INDIV

            if st.session_state.user_logs["classificacao_Angiotomografia"] != None:
                fangio = st.session_state.user_logs["classificacao_Angiotomografia"]
            else:
                fangio = ANGIOTOMOGRAFIA_CONCLUSAO_INDIV

            finalri = finish_ri(cpf_cliente = NR_CPF,
                            dh_laudo_ri = datatoday,
                            ds_url_laudo_ri = f"ri-cardio/relatorio-integrado-pdf/{output_pdf_path}",
                            in_ri_finalizado = True,
                            nr_acession_numbers = [ERGOMETRIA_CLRI_NR_ACESSION_NUMBER, CINTILOGRAFIA_CLRI_NR_ACESSION_NUMBER, ANGIOTOMOGRAFIA_CLRI_NR_ACESSION_NUMBER],
                            sg_cate_medico_ri = "CRM",
                            nr_cert_medico_ri = CRM,
                            uf_cert_medico_ri = UF_CRM,
                            ds_conclusao_md = [fergo, fcint, fangio], 
                            client = client)
                
            st.markdown(finalri)

    else:
        if st.button("Save RI"):
            nome_medico = MEDICO
            option_ficha = ERGOMETRIA_FICHA
            cliente = CLRI_NR_CLIENTE
            sexo = CLRI_SL_SEXO
            birthdate = CLRI_DT_NASCTO
            idade = calculate_age(birthdate)
            output_pdf_path = create_ri(
                option_ficha, nome_medico, option_cliente, cliente, sexo, idade, ci
            )

            blob = bucket.blob(f"ri-cardio/relatorio-integrado-pdf/{output_pdf_path}")
            blob.upload_from_filename(output_pdf_path)

            show_pdf(output_pdf_path)

            if finalergo == True:
                crm_ergo = CRM
                state_md_ergo = UF_CRM
                if st.session_state.user_logs["classificacao_Ergometria"] != None:
                    fergo = st.session_state.user_logs["classificacao_Ergometria"]
                else:
                    fergo = ERGOMETRIA_CONCLUSAO_INDIV

                upexames = update_exames(cpf_cliente = NR_CPF,
                            dh_laudo_ri = datatoday,
                            ds_url_laudo_ri = f"ri-cardio/relatorio-integrado-pdf/{output_pdf_path}",
                            in_ri_finalizado = "FALSE",
                            nr_acession_numbers = ERGOMETRIA_CLRI_NR_ACESSION_NUMBER,
                            no_subgrupo_values = "ERGOMETRIA",
                            sg_cate_medico_ri = "CRM",
                            nr_cert_medico_ri = crm_ergo,
                            uf_cert_medico_ri_values = state_md_ergo,
                            ds_conclusao_ia_values = fergo,
                            ds_conclusao_md_values = fergo,
                            client = client)
                st.markdown(upexames)
            else:
                crm_ergo = " "
                state_md_ergo = " "
                if st.session_state.user_logs["classificacao_Ergometria"] != None:
                    fergo = st.session_state.user_logs["classificacao_Ergometria"]
                else:
                    fergo = ERGOMETRIA_CONCLUSAO_INDIV

            if finalcint == True:
                crm_cint = CRM
                state_md_cint = UF_CRM
                if st.session_state.user_logs["classificacao_Cintilografia"] != None:
                    fcint = st.session_state.user_logs["classificacao_Cintilografia"]
                else:
                    fcint = CINTILOGRAFIA_CONCLUSAO_INDIV

                upexames = update_exames(cpf_cliente = NR_CPF,
                            dh_laudo_ri = datatoday,
                            ds_url_laudo_ri = f"ri-cardio/relatorio-integrado-pdf/{output_pdf_path}",
                            in_ri_finalizado = "FALSE",
                            nr_acession_numbers = CINTILOGRAFIA_CLRI_NR_ACESSION_NUMBER,
                            no_subgrupo_values = "CINTILOGRAFIA ASSOCIADA A STRESS",
                            sg_cate_medico_ri = "CRM",
                            nr_cert_medico_ri = crm_cint,
                            uf_cert_medico_ri_values = state_md_cint,
                            ds_conclusao_ia_values = fcint,
                            ds_conclusao_md_values = fcint,
                            client = client)
                st.markdown(upexames)

            else:
                crm_cint = ""
                state_md_cint = ""
                if st.session_state.user_logs["classificacao_Cintilografia"] != None:
                    fcint = st.session_state.user_logs["classificacao_Cintilografia"]
                else:
                    fcint = CINTILOGRAFIA_CONCLUSAO_INDIV

            if finalangio == True:
                crm_angio = CRM
                state_md_angio = UF_CRM
                if st.session_state.user_logs["classificacao_Angiotomografia"] != None:
                    fangio = st.session_state.user_logs["classificacao_Angiotomografia"]
                else:
                    fangio = ANGIOTOMOGRAFIA_CONCLUSAO_INDIV

                upexames = update_exames(cpf_cliente = NR_CPF,
                            dh_laudo_ri = datatoday,
                            ds_url_laudo_ri = f"ri-cardio/relatorio-integrado-pdf/{output_pdf_path}",
                            in_ri_finalizado = "FALSE",
                            nr_acession_numbers = ANGIOTOMOGRAFIA_CLRI_NR_ACESSION_NUMBER,
                            no_subgrupo_values = "ANGIOTOMOGRAFIA DE CORONÁRIAS",
                            sg_cate_medico_ri = "CRM",
                            nr_cert_medico_ri = crm_angio,
                            uf_cert_medico_ri_values = state_md_angio,
                            ds_conclusao_ia_values = fangio,
                            ds_conclusao_md_values = fangio,
                            client = client) 
                    
                st.markdown(upexames)
            else:
                crm_angio = ""
                state_md_angio = ""
                fangio = ANGIOTOMOGRAFIA_CONCLUSAO_INDIV
                if st.session_state.user_logs["classificacao_Angiotomografia"] != None:
                    fangio = st.session_state.user_logs["classificacao_Angiotomografia"]
                else:
                    fangio = ANGIOTOMOGRAFIA_CONCLUSAO_INDIV

            if st.button("Voltar para o Dashboard"):
                st.session_state.show_second_page = False
                st.rerun()
        