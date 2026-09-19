import os
import httpx

from apiKey_apiURL import OCR_API_KEY, OCR_API_URL

from fastapi import (
    UploadFile,
    HTTPException
)

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