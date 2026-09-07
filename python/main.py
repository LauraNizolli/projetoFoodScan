from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException
)

import re

from pydantic import BaseModel

from regras import regras

import unicodedata

from gemini_ia import verificar_com_ia


# ==========================
# OCR
# ==========================

import os
import httpx

from dotenv import load_dotenv


load_dotenv()


OCR_API_KEY = os.getenv(
    "OCR_SPACE_API_KEY"
)

OCR_API_URL = (
    "https://api.ocr.space/parse/image"
)


app = FastAPI()


# ==========================
# MODELO
# ==========================

class Dados(BaseModel):

    nome_produto: str

    ingredientes: str

    advertencias: str

    restricoes: list[str]


# ==========================
# NORMALIZAÇÃO
# ==========================

def normalizar(texto):

    texto = texto.strip().lower()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        letra
        for letra in texto
        if unicodedata.category(letra)
        != "Mn"
    )

    return texto


# ==========================
# GEMINI
# ==========================

def analisar_com_ia(resposta: dict):

    resposta_ia = verificar_com_ia(
        resposta
    )

    return {
        "analise_regras": resposta,
        "analise_ia": resposta_ia
    }


# ==========================
# OCR.SPACE
# ==========================

async def executar_ocr(
    imagem: UploadFile
):
    
    print("OCR encontrada:", bool(os.getenv("OCR_SPACE_API_KEY")))

    # Verifica se a chave existe
    if not OCR_API_KEY:

        raise HTTPException(
            status_code=500,
            detail=(
                "Chave da OCR.Space "
                "não encontrada."
            )
        )


    # Lê o arquivo enviado
    conteudo = await imagem.read()


    # Chave da API
    headers = {
        "apikey": OCR_API_KEY
    }


    # Arquivo enviado para OCR.Space
    files = {
        "file": (
            imagem.filename,
            conteudo,
            imagem.content_type
        )
    }


    # Configurações da OCR
    data = {
        "language": "por",
        "OCREngine": "2",
        "isOverlayRequired": "false",
        "detectOrientation": "true",
        "scale": "true"
    }


    # Envia a imagem para a OCR.Space
    async with httpx.AsyncClient(
        timeout=60.0
    ) as client:

        resposta = await client.post(
            OCR_API_URL,
            headers=headers,
            files=files,
            data=data
        )


    # Verifica erros HTTP
    resposta.raise_for_status()


    # Converte resposta JSON
    resultado = resposta.json()


    # Verifica erro informado pela OCR
    if resultado.get(
        "IsErroredOnProcessing"
    ):

        raise HTTPException(
            status_code=400,
            detail=resultado.get(
                "ErrorMessage",
                "Erro ao processar imagem."
            )
        )


    # Pega resultados encontrados
    parsed_results = resultado.get(
        "ParsedResults",
        []
    )


    # Se não encontrou texto
    if not parsed_results:

        raise HTTPException(
            status_code=400,
            detail=(
                "Nenhum texto encontrado "
                "na imagem."
            )
        )


    # Pega o texto reconhecido
    texto = parsed_results[0].get(
        "ParsedText",
        ""
    )


    return texto


# ==========================
# EXTRAIR DADOS DO RÓTULO
# ==========================

def extrair_dados_rotulo(
    texto_ocr
):

    # ==========================
    # LIMPEZA
    # ==========================

    texto = texto_ocr.replace(
        "\r",
        " "
    )

    texto = texto.replace(
        "\n",
        " "
    )

    texto = " ".join(
        texto.split()
    )


    texto_normalizado = normalizar(texto)


    ingredientes = ""

    advertencias = ""


    print(texto_normalizado)

    # ==========================
    # EXTRAIR INGREDIENTES
    # ==========================

    inicio_ingredientes = -1


    if "ingredientes:" in texto_normalizado:

        inicio_ingredientes = (
            texto_normalizado.find(
                "ingredientes:"
            )
            +
            len("ingredientes:")
        )

        

    elif "ingr.:" in texto_normalizado:

        inicio_ingredientes = (
            texto_normalizado.find(
                "ingr.:"
            )
            +
            len("ingr.:")
        )

    print(inicio_ingredientes)


    # Se encontrou ingredientes
    if inicio_ingredientes != -1:

        fim_ingredientes = len(
            texto
        )


        # Marcadores que podem aparecer
        # DEPOIS dos ingredientes
        palavras_fim_ingredientes = [

            "nao contem",

            "contem",


            "alergicos:",

            "pode conter",

            "informacao nutricional"
        ]

        posicaoOficial = 0

        for palavra in palavras_fim_ingredientes:

            if palavra == "nao contem":

            # IMPORTANTE:
            # procura SOMENTE depois
            # do início dos ingredientes
                posicaoOficial = (
                    texto_normalizado.find(
                        palavra,
                        inicio_ingredientes
                    )
                )
                print(posicaoOficial)
            else:
                posicaoProv = (
                    texto_normalizado.find(
                        palavra, 
                        inicio_ingredientes
                    )
                )

                print(posicaoProv)

                if ((posicaoProv < posicaoOficial) and (posicaoProv != -1)) or (posicaoOficial == -1):
                    posicaoOficial = posicaoProv

    

        print(posicaoOficial)

        if ( posicaoOficial != -1 and posicaoOficial < fim_ingredientes):
            
            fim_ingredientes = (posicaoOficial)


            ingredientes = texto[
                inicio_ingredientes:
                fim_ingredientes
            ].strip()
    else:
        raise HTTPException(
                    status_code=400,
                    detail=(
                        "Nenhum texto encontrado como inicio da lista de ingredientes."
                    )
                )


    # ==========================
    # EXTRAIR ADVERTÊNCIAS
    # ==========================

    # Primeiro tenta localizar
    # ALÉRGICOS:
    inicio_advertencias = fim_ingredientes


    # ==========================
    # DEFINIR FIM DAS ADVERTÊNCIAS
    # ==========================

    if inicio_advertencias != -1:

        fim_advertencias = len(
            texto
        )


        palavras_fim_advertencias = [

            "informacao nutricional",

            "porcao",

            "valor energetico",

            "modo de conservação"
        ]



            # IMPORTANTE:
            # procura somente DEPOIS
            # do início das advertências
        posicaoOficial = 0
            
        for palavra in palavras_fim_advertencias:
            
            if palavra == "informacao nutricional":
            
                # IMPORTANTE:
                # procura SOMENTE depois             
                posicaoOficial = texto_normalizado.find(
                    palavra,
                    inicio_ingredientes
                    )
                
            else:
                posicaoProv = (
                texto_normalizado.find(
                palavra, 
                inicio_ingredientes
                )
                )
            
                if ((posicaoProv < posicaoOficial) and (posicaoProv == -1)) or (posicaoOficial == -1):
                    posicaoOficial = posicaoProv

        if ( posicaoOficial != -1 and posicaoOficial < fim_advertencias):
                    
                    fim_advertencias = (posicaoOficial)
            


        advertencias = texto[
            inicio_advertencias:
            fim_advertencias
        ].strip()


    # ==========================
    # RETORNO
    # ==========================

    return {

        "ingredientes":
            ingredientes,

        "advertencias":
            advertencias
    }


# ==========================
# ANÁLISE
# ==========================

def executar_analise(
    nome_produto,
    ingredientes,
    advertencias,
    restricoes
):

    # ==========================
    # PREPARAR INGREDIENTES
    # ==========================

    lista_ingredientes = [ 
        normalizar(i) for i in re.split(r"\s*,\s*|\s*;\s*|\s*\.\s*|\s+e\s+|\s*:\s*", ingredientes)
    ]

    print(lista_ingredientes)

    # ==========================
    # PREPARAR ADVERTÊNCIAS
    # ==========================

    lista_advertencias = [
        normalizar (i) for i in re.split(r"\s*,\s*|\s*;\s*|\s*\.\s*|\s+E\s+|\s*:\s*", advertencias)
    ]

    print(lista_advertencias)

    # ==========================
    # PREPARAR RESTRIÇÕES
    # ==========================

    lista_restricoes = [
        normalizar(r)
        for r
        in restricoes
    ]


    motivos = []


    # ==========================
    # ANALISAR INGREDIENTES
    # ==========================

    for ingrediente in lista_ingredientes:

        if ingrediente in regras:

            restricao_necessaria = (
                regras[
                    ingrediente
                ]["restricao"]
            )


            if (
                restricao_necessaria
                in
                lista_restricoes
            ):

                mensagem = (
                    regras[
                        ingrediente
                    ]["mensagem"]
                )


                if mensagem not in motivos:

                    motivos.append(
                        mensagem
                    )


    # ==========================
    # ANALISAR ADVERTÊNCIAS
    # ==========================

    for ingrediente, dados_regra in regras.items():


        # Procura o ingrediente
        # dentro das advertências
        if (
            ingrediente
            in
            lista_advertencias
        ):

            restricao_necessaria = (
                dados_regra[
                    "restricao"
                ]
            )


            if (
                restricao_necessaria
                in
                lista_restricoes
            ):

                mensagem = (
                    dados_regra[
                        "mensagem"
                    ]
                )


                if mensagem not in motivos:

                    motivos.append(
                        mensagem
                    )


    # ==========================
    # RESULTADO
    # ==========================

    if motivos:

        resposta = {

            "produto":
                nome_produto,

            "ingredientes":
                ingredientes,

            "advertencias":
                advertencias,

            "restricoes":
                restricoes,

            "resultado":
                "não recomendado",

            "motivos":
                motivos
        }


    else:

        resposta = {

            "produto":
                nome_produto,

            "ingredientes":
                ingredientes,

            "advertencias":
                advertencias,

            "restricoes":
                restricoes,

            "resultado":
                "seguro para consumo",

            "motivos":
                []
        }


    return resposta


# ==========================
# HOME
# ==========================

@app.get("/")
def home():

    return {
        "Mensagem":
            "FoodScan funcionando!"
    }


# ==========================
# ANÁLISE POR TEXTO
# ==========================

@app.post("/analisar")
def analisar(
    nome_produto: str = Form(...),
    ingredientes: str = Form(...),
    advertencias: str = Form(...),
    restricoes: str = Form(...)
):

    return executar_analise(

        nome_produto,

        ingredientes,

        advertencias,

        restricoes
    )


# ==========================
# ANÁLISE POR IMAGEM
# ==========================

@app.post("/analisar-imagem")
async def analisar_imagem(

    imagem: UploadFile = File(...),

    nome_produto: str = Form(...),

    restricoes: str = Form(...)
):

    # ==========================
    # 1. OCR
    # ==========================

    texto_ocr = await executar_ocr(
        imagem
    )


    # ==========================
    # 2. EXTRAIR RÓTULO
    # ==========================

    dados_rotulo = (
        extrair_dados_rotulo(
            texto_ocr
        )
    )


    ingredientes = (
        dados_rotulo[
            "ingredientes"
        ]
    )


    advertencias = (
        dados_rotulo[
            "advertencias"
        ]
    )


    # ==========================
    # 3. RESTRIÇÕES DO USUÁRIO
    # ==========================

    lista_restricoes = [
        r.strip()
        for r
        in restricoes.split(",")
    ]


    # ==========================
    # 4. ANÁLISE
    # ==========================

    analise = executar_analise(

        nome_produto,

        ingredientes,

        advertencias,

        lista_restricoes
    )


    # ==========================
    # 5. RETORNO FINAL
    # ==========================

    return {

        "texto_ocr":
            texto_ocr,

        "ingredientes_extraidos":
            ingredientes,

        "advertencias_extraidas":
            advertencias,

        "analise":
            analise
    }
    # ==========================
    # Terminamosss (????)
    # ==========================