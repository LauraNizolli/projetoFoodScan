from normalizarFunc import normalizar
import re
from regras import regras
from gemini_ia import analisar_com_ia

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
        normalizar(i) for i in re.split(r"\s*,\s*|\s*;\s*|\s*\.\s*|\s+e\s+|\s+E\s+|\s*:\s*|\s*\(\s*|\s*\)\s*", ingredientes)
    ]

    print(lista_ingredientes)

    # ==========================
    # PREPARAR ADVERTÊNCIAS
    # ==========================

    lista_advertencias = [
        normalizar (i) for i in re.split(r"\s*,\s*|\s*;\s*|\s*\.\s*|\s+e\s+|\s+E\s+|\s*:\s*|\s*\(\s*|\s*\)\s*", advertencias)
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


    return analisar_com_ia(resposta)