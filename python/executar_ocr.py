import os
import httpx

from io import BytesIO
from PIL import Image, ImageOps

from apiKey_apiURL import OCR_API_KEY, OCR_API_URL

from fastapi import (
    UploadFile,
    HTTPException
)

def reduzir_imagem(conteudo: bytes) -> bytes:

    # Abre a imagem que está armazenada em bytes
    with Image.open(BytesIO(conteudo)) as imagem:

        # Corrige a orientação de fotos tiradas pelo celular
        imagem = ImageOps.exif_transpose(imagem)

        # Converte a imagem para RGB
        # Isso permite salvá-la no formato JPEG
        imagem = imagem.convert("RGB")

        # Reduz as dimensões mantendo a proporção
        imagem.thumbnail((1600, 1600))

        # Começa tentando salvar com qualidade 85
        qualidade = 85

        # Inicializa a variavel
        conteudo_reduzido = conteudo

        # Vai diminuindo a qualidade até chegar em 35
        while qualidade >= 35:

            # Cria um espaço temporário na memória
            saida = BytesIO()

            # Salva a imagem em JPEG nesse espaço temporário
            imagem.save(
                saida,
                format="JPEG",
                quality=qualidade,
                optimize=True
            )

            # Pega a imagem reduzida em formato de bytes
            conteudo_reduzido = saida.getvalue()

            # Verifica se ficou abaixo de 900 KB
            if len(conteudo_reduzido) <= 950_000:

                return conteudo_reduzido

            # Se ainda estiver grande, diminui a qualidade
            qualidade -= 10

        # Retorna a última versão gerada
        return conteudo_reduzido


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

    # Reduz a imagem antes de enviá-la para a OCR.Space
    conteudo = reduzir_imagem(conteudo)


    # Chave da API
    headers = {
        "apikey": OCR_API_KEY
    }


    # Arquivo enviado para OCR.Space
    files = {
        "file": (
            "imagem_reduzida.jpg",
            conteudo,
            "imagem/jpeg"
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