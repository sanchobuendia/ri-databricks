import pandas as pd
import datetime
import base64
import streamlit as st
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    PageBreak,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
import os
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from google.cloud import storage
from google.oauth2 import service_account
import json
import numpy as np
from datetime import datetime, date
import glob

credentials = service_account.Credentials.from_service_account_file('ped-dev.json')
storage_client = storage.Client(credentials=credentials)
bucket = storage_client.bucket("ped-dev-dados")


def conclusao_integrada(classes, regras_conclusao_integrada):
    """Esta função retorna a conclusão integrada do exame.
    param df: DataFrame com os dados do exame. Apenas 3 linhas.
    param regras_conclusao_integrada: DataFrame com as regras para a conclusão integrada.
    """

    for k in range(0, len(regras_conclusao_integrada)):
        if (
            (
                classes[0].strip() == regras_conclusao_integrada.iloc[k, 0].strip()
            )
            & (
                classes[1].strip() == regras_conclusao_integrada.iloc[k, 1].strip()
            )
            & (
                classes[2].strip() == regras_conclusao_integrada.iloc[k, 2].strip()
            )
        ):
            return regras_conclusao_integrada.iloc[k, 3]


def show_pdf(file_path: str):
    """Esta função exibe o arquivo pdf do RI no streamlit.
    param file_path: Caminho do arquivo pdf.
    """
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")

    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def calculate_age(birthdate: str):
    """Esta função calcula a idade em anos."""
    current_date = date.today()
    birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
    age = (
        current_date.year
        - birthdate.year
        - (
            (current_date.month, current_date.day)
            < (birthdate.month, birthdate.day)
        )
    )

    return age


def save_uploaded_image(uploaded_file: io.BytesIO):
    """Esta função salva a imagem no diretório saved_images.
    param uploaded_file: Imagem carregada pelo usuário.
    """
    if not os.path.exists("saved_images"):
        os.makedirs("saved_images")
    image = Image.open(uploaded_file)
    filename = f"saved_images/{uploaded_file.name}"
    image.save(filename)


def create_folder_if_not_exists(folder_path: str):
    """Esta função cria uma pasta se ela não existir.
    param folder_path: Caminho da pasta.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def save_uploaded_file(upload_folder: str, uploaded_file: str):
    """Esta função salva o arquivo no diretório upload_folder.
    param upload_folder: Caminho da pasta.
    param uploaded_file: Arquivo carregado pelo usuário.
    """
    file_path = os.path.join(upload_folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def create_pdf_from_images(image_paths: str, story: object):
    """Esta função cria um pdf a partir de imagens.
    param image_paths: Lista com os caminhos das imagens.
    param story: Objeto story do reportlab.
    """
    for image_path in image_paths:
        blob = bucket.blob(image_path)
        content = blob.download_as_bytes()
        story.append(Image(io.BytesIO(content), 1 * 200, 1 * 200, hAlign="CENTER"))

        # Image('fleury_logo.png', 1*200, 1*100, hAlign="LEFT")

    return story


def cabecalho(
    story: object,
    ficha: str,
    data: str,
    md: str,
    cliente: str,
    idade: int,
    sexo: str,
    idendificacao: str,
    dados_clinicos: str,
):
    """Esta função cria o cabeçalho do RI.
    param story: Objeto story do reportlab.
    param ficha: Número da ficha.
    param date: Data do exame.
    param md: Nome do médico.
    param cliente: Nome do cliente.
    param idade: Idade do cliente.
    param sexo: Sexo do cliente.
    param idendificacao: Identificação do cliente.
    param dados_clinicos: Dados clínicos do cliente.
    """

    story.append(Image("fleury_logo.png", 1 * 200, 1 * 100, hAlign="LEFT"))

    #############################################################################
    spacer_between_tables = Spacer(width=0, height=-25)
    story.append(spacer_between_tables)
    #############################################################################

    table_style = TableStyle(
        [
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 1), (-1, -1), 1, colors.black),
        ]
    )

    table_style2 = TableStyle(
        [
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 1), (-1, -1), 1, colors.black),
        ]
    )

    tb0 = [[" "], [" "]]

    tb1 = [[" "], [f"FICHA: {ficha}"]]

    tb2 = [[" "], [f"Data: {data}"]]

    tb3 = [[" "], [f"Médico: {md}"]]

    tb5 = [[" "], [f"IDADE: {idade}"]]

    tb6 = [[" "], [f"SEXO: {sexo}"]]

    tb7 = [[" "], [f"CLIENTE: {idendificacao}"]]

    tb8 = [[" "], [f"Dados Clínicos: {dados_clinicos}"]]

    tb0 = Table(tb0, colWidths=[50, 50, 50], rowHeights=20)

    #############################################################################

    tb1 = Table(tb1, colWidths=[110, 100, 100], rowHeights=20)
    tb1.setStyle(table_style)

    tb2 = Table(tb2, colWidths=[110, 100, 100], rowHeights=20)
    tb2.setStyle(table_style)

    row_data = [[tb0, tb0, tb1, tb2]]

    row_table = Table(row_data, colWidths=[115, 115], rowHeights=10)
    row_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(row_table)

    #############################################################################

    tb3 = Table(tb3, colWidths=[464, 100, 100], rowHeights=20)
    tb3.setStyle(table_style2)
    story.append(tb3)

    #############################################################################
    spacer_between_tables = Spacer(width=0, height=-5)
    story.append(spacer_between_tables)
    #############################################################################

    tb5 = Table(tb5, colWidths=[60, 100, 100], rowHeights=20)
    tb5.setStyle(table_style)

    tb6 = Table(tb6, colWidths=[60, 100, 100], rowHeights=20)
    tb6.setStyle(table_style)

    tb7 = Table(tb7, colWidths=[140, 100, 100], rowHeights=20)
    tb7.setStyle(table_style)

    row_data = [[tb5, tb6, tb7]]

    row_table = Table(row_data, colWidths=[123, 200, 154], rowHeights=20)
    row_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(row_table)

    #############################################################################
    spacer_between_tables = Spacer(width=0, height=-5)
    story.append(spacer_between_tables)
    #############################################################################

    tb8 = Table(tb8, colWidths=[464, 100, 100], rowHeights=20)
    tb8.setStyle(table_style2)
    story.append(tb8)

    #############################################################################
    spacer_between_tables = Spacer(width=0, height=20)
    story.append(spacer_between_tables)
    #############################################################################

    return story


def create_ri(
    option_ficha: str,
    nome_medico: str,
    option_cliente: str,
    cliente: str,
    sexo: str,
    idade: str,
    ci: str,
):
    """Esta função cria o RI.
    param option_ficha: Número da ficha.
    param nome_medico: Nome do médico.
    param option_cliente: Identificação do cliente.
    param cliente: Nome do cliente.
    param sexo: Sexo do cliente.
    param idade: Idade do cliente.
    param ci: Conclusão integrada.
    """

    story = []
    data = date.today()
    dados_clinicos = "Avaliação Cardiológica"

    folder_path = f"ri-cardio/clientes/{option_cliente}/ergometria/"
    image_paths1 = bucket.list_blobs(prefix=folder_path)
    image_paths1 = [
        file.name for file in image_paths1 if file.name.lower().endswith(".png")
    ]

    folder_path = f"ri-cardio/clientes/{option_cliente}/cintilografia/"
    image_paths2 = bucket.list_blobs(prefix=folder_path)
    image_paths2 = [
        file.name for file in image_paths2 if file.name.lower().endswith(".png")
    ]

    folder_path = f"ri-cardio/clientes/{option_cliente}/angiotomografia/"
    image_paths3 = bucket.list_blobs(prefix=folder_path)
    image_paths3 = [
        file.name for file in image_paths3 if file.name.lower().endswith(".png")
    ]

    tipo_CLRI_NO_SUBGRUPO = "Teste Ergométrico"

    story = cabecalho(
        story,
        option_ficha,
        data,
        nome_medico,
        cliente,
        idade,
        sexo,
        option_cliente,
        dados_clinicos,
    )

    styles = getSampleStyleSheet()
    header_paragraph = Paragraph("Conclusão", styles["Heading1"])
    story.append(header_paragraph)
    conclusion = Paragraph(ci, styles["Heading3"])
    story.append(conclusion)

    styles = getSampleStyleSheet()
    header_paragraph = Paragraph(f"Teste Ergométrico", styles["Heading1"])
    story.append(header_paragraph)

    story = create_pdf_from_images(image_paths1, story)

    story.append(PageBreak())

    story = cabecalho(
        story,
        option_ficha,
        data,
        nome_medico,
        cliente,
        idade,
        sexo,
        option_cliente,
        dados_clinicos,
    )
    styles = getSampleStyleSheet()
    header_paragraph = Paragraph(
        f"Cintilografia Miocárdica", styles["Heading1"]
    )
    story.append(header_paragraph)

    story = create_pdf_from_images(image_paths2, story)

    story.append(PageBreak())

    story = cabecalho(
        story,
        option_ficha,
        data,
        nome_medico,
        cliente,
        idade,
        sexo,
        option_cliente,
        dados_clinicos,
    )
    styles = getSampleStyleSheet()
    header_paragraph = Paragraph(f"Tomografia Coronária", styles["Heading1"])
    story.append(header_paragraph)

    story = create_pdf_from_images(image_paths3, story)

    output_pdf_path = f"{option_cliente}_RelatorioIntegrado.pdf"
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    doc.build(story)

    return output_pdf_path


def registrar_uso_servico(id: str, usuario: str, servico: str):
    """Registra o uso de um serviço por um usuário."""
    data_hora_atual = datetime.now()
    data_hora_formatada = data_hora_atual.strftime("%Y-%m-%d %H:%M:%S")

    registro = {"id": id,"Usuario": usuario, "Hora": data_hora_formatada, "Servico": servico}

    try:
        with open("log.json", "a") as arquivo_json:
            json.dump(registro, arquivo_json)
            arquivo_json.write("\n")

    except FileNotFoundError:
        with open("log.json", "w") as arquivo_json:
            json.dump(registro, arquivo_json)
            arquivo_json.write("\n")

def registrar_upstade_class(id: str, usuario: str, classification: str, name: str):
    """Registra o uso de um serviço por um usuário."""
    data_hora_atual = datetime.now()
    data_hora_formatada = data_hora_atual.strftime("%Y-%m-%d %H:%M:%S")

    registro = {"id": id,"Usuario": usuario, "Hora": data_hora_formatada, "classification": classification}

    if os.path.exists(name):
        os.remove(name)
        with open(name, 'w') as arquivo_json:
            pass
    else:
        with open(name, 'w') as arquivo_json:
            pass

    try:
        with open(name, "a") as arquivo_json:
            json.dump(registro, arquivo_json)
            arquivo_json.write("\n")

    except FileNotFoundError:
        with open(name, "w") as arquivo_json:
            json.dump(registro, arquivo_json)
            arquivo_json.write("\n")
