from fastapi import UploadFile, File, Form
from executar_ocr import executar_ocr
from executar_analise import executar_analise
from extrairImg import extrair_dados_rotulo



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