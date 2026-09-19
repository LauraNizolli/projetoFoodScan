from normalizarFunc import normalizar
from fastapi import HTTPException 

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


    if "ingredientes" in texto_normalizado:

        inicio_ingredientes = (
            texto_normalizado.find(
                "ingredientes"
            )
            +
            len("ingredientes")
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