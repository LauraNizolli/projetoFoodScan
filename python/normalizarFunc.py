
import unicodedata

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