from normalizarFunc import normalizar
import re
from regras import regras
from gemini_ia import analisar_com_ia_gemini

# ==========================
# ANÁLISE
# ==========================

def executar_analise(
    texto_ocr,
    ingredientes,
    advertencias,
    restricoes
):

    # ==========================
    # PREPARAR INGREDIENTES
    # ==========================

    lista_ingredientes = [ 
        normalizar(i) for i in re.split(r"\s*,\s*|\s*;\s*|\s*\.\s*|\s*:\s*|\s*\(\s*|\s*\)\s*", ingredientes)
    ]

    print(lista_ingredientes)

    # ==========================
    # PREPARAR ADVERTÊNCIAS
    # ==========================

    lista_advertencias = [
        normalizar (i) for i in re.split(r"\s*,\s*|\s*;\s*|\s*\.\s*|\s*:\s*|\s*\(\s*|\s*\)\s*", advertencias)
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
                ]["restricoes"]
            )


            if any(
            restricao in lista_restricoes
            for restricao in restricao_necessaria
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

            restricao_necessaria = dados_regra["restricoes"]

            if any(
            restricao in lista_restricoes
            for restricao in restricao_necessaria
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
                
            "texto original da OCR":
                texto_ocr,

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
                
            "texto original da OCR":
                texto_ocr,

            "ingredientes":
                ingredientes,

            "advertencias":
                advertencias,

            "restricoes":
                restricoes,

            "resultado":
                "não foram identificados riscos",

            "motivos":
                []
        }


    return analisar_com_ia_gemini(resposta)