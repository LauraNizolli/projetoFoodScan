from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException
)

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


    # Arquivo que será enviado
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


    # Caso a própria requisição HTTP dê erro
    resposta.raise_for_status()


    # Converte a resposta para JSON
    resultado = resposta.json()


    # Verifica se a OCR informou erro
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


    # Pega os resultados da OCR
    parsed_results = resultado.get(
        "ParsedResults",
        []
    )


    # Verifica se encontrou algum texto
    if not parsed_results:

        raise HTTPException(
            status_code=400,
            detail=(
                "Nenhum texto encontrado "
                "na imagem."
            )
        )


    # Pega somente o texto reconhecido
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

    # --------------------------
    # LIMPEZA DO TEXTO
    # --------------------------

    # Remove retorno de carro
    texto = texto_ocr.replace(
        "\r",
        " "
    )

    # Remove quebra de linha
    texto = texto.replace(
        "\n",
        " "
    )

    # Remove espaços duplicados
    texto = " ".join(
        texto.split()
    )


    # Cria uma cópia em minúsculas
    # para facilitar as buscas
    texto_minusculo = texto.lower()


    # Variáveis onde vamos guardar
    # as informações encontradas
    ingredientes = ""
    alergicos = ""


    # ==========================
    # EXTRAIR INGREDIENTES
    # ==========================

    if "ingredientes:" in texto_minusculo:

        # Descobre onde termina
        # a palavra INGREDIENTES:
        inicio_ingredientes = (
            texto_minusculo.find(
                "ingredientes:"
            )
            +
            len("ingredientes:")
        )


        # Inicialmente consideramos
        # que vai até o fim do texto
        fim_ingredientes = len(
            texto
        )

    elif "ingr.:" in texto_minusculo:
        inicio_ingredientes = (
            texto_minusculo.find(
                "ingr.:"
            )
            +
            len("ingr.:")
        )


        # Palavras que podem indicar
        # que a parte dos ingredientes acabou
        palavras_fim = [
            "alérgicos:",
            "alergicos:",
            "contém",
            "contem",
            "não contém",
            "nao contem",
            "pode conter"
        ]


        # Procura cada possível marcador
        for palavra in palavras_fim:

            posicao = (
                texto_minusculo.find(
                    palavra,
                    inicio_ingredientes
                )
            )


            # Se encontrou a palavra
            # e ela aparece antes do
            # fim atual
            if (
                posicao != -1
                and
                posicao < fim_ingredientes
            ):

                fim_ingredientes = (
                    posicao
                )


        # Recorta somente os ingredientes
        ingredientes = texto[
            inicio_ingredientes:
            fim_ingredientes
        ].strip()


    # ==========================
    # EXTRAIR ALÉRGICOS
    # ==========================

    # -1 significa:
    # ainda não encontramos
    inicio_alergicos = -1


    # Primeiro procura com acento
    if "alérgicos:" in texto_minusculo:

        inicio_alergicos = (
            texto_minusculo.find(
                "alérgicos:"
            )
            +
            len("alérgicos:")
        )


    # Se não encontrar,
    # procura sem acento
    elif "alergicos:" in texto_minusculo:

        inicio_alergicos = (
            texto_minusculo.find(
                "alergicos:"
            )
            +
            len("alergicos:")
        )


    # Se encontrou ALÉRGICOS:
    if inicio_alergicos != -1:

        # Inicialmente consideramos
        # que vai até o fim do texto
        fim_alergicos = len(
            texto
        )


        # Recorta somente a parte
        # que vem depois de ALÉRGICOS:
        alergicos = texto[
            inicio_alergicos:
            fim_alergicos
        ].strip()


    # Devolve os dois resultados
    return {
        "ingredientes": ingredientes,
        "alergicos": alergicos
    }


# ==========================
# ANÁLISE
# ==========================

def executar_analise(
    nome_produto,
    ingredientes,
    restricoes
):

    # Separa os ingredientes
    # usando a vírgula
    lista_ingredientes = [
        normalizar(i)
        for i
        in ingredientes.split(",")
    ]


    # Normaliza as restrições
    restricoes_normalizadas = [
        normalizar(r)
        for r
        in restricoes
    ]


    motivos = []


    # Percorre todos os ingredientes
    for ingrediente in lista_ingredientes:

        # Verifica se existe
        # no dicionário regras
        if ingrediente in regras:

            restricao_necessaria = (
                regras[
                    ingrediente
                ]["restricao"]
            )


            # Verifica se o usuário
            # possui essa restrição
            if (
                restricao_necessaria
                in
                restricoes_normalizadas
            ):

                motivos.append(
                    regras[
                        ingrediente
                    ]["mensagem"]
                )


    # Se encontrou algum problema
    if motivos:

        resposta = {

            "produto":
                nome_produto,

            "ingredientes":
                ingredientes,

            "restricoes":
                restricoes,

            "resultado":
                "não recomendado",

            "motivos":
                motivos
        }


    # Se não encontrou problemas
    else:

        resposta = {

            "produto":
                nome_produto,

            "ingredientes":
                ingredientes,

            "restricoes":
                restricoes,

            "resultado":
                "seguro para consumo",

            "motivos":
                []
        }


    # Depois das regras,
    # envia também para a IA
    return analisar_com_ia(
        resposta
    )


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
    dados: Dados
):

    return executar_analise(

        dados.nome_produto,

        dados.ingredientes,

        dados.restricoes
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

    # --------------------------
    # 1. OCR
    # --------------------------

    texto_ocr = await executar_ocr(
        imagem
    )


    # --------------------------
    # 2. SEPARAR RÓTULO
    # --------------------------

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


    alergicos = (
        dados_rotulo[
            "alergicos"
        ]
    )


    # --------------------------
    # 3. RESTRIÇÕES
    # --------------------------

    # No Swagger você pode escrever:
    #
    # gluten,lactose,soja

    lista_restricoes = [
        r.strip()
        for r
        in restricoes.split(",")
    ]


    # --------------------------
    # 4. ANÁLISE
    # --------------------------

    analise = executar_analise(

        nome_produto,

        ingredientes,

        lista_restricoes
    )


    # --------------------------
    # 5. RESULTADO FINAL
    # --------------------------

    return {

        "texto_ocr":
            texto_ocr,

        "ingredientes_extraidos":
            ingredientes,

        "alergicos_extraidos":
            alergicos,

        "analise":
            analise
    }