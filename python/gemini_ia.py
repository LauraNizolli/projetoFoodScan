import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def verificar_com_ia(resultado_regras):
    prompt = f"""
Você é uma IA que ajuda a revisar uma análise de ingredientes para restrições alimentares.

Este foi o JSON gerado pelo sistema:

{resultado_regras}

Leve em consideração para os passos a seguir todos os "motivos" que foram listado no json, e preencha lacunas deixadas por essa análise, caso extritamente necessário, 
não adicione informações a essa análise que não sejam muito relevantes e extritamente necessárias.
Analise cada ingrediente e advertência separadamente e veja se ele apresenta uma relação com cada uma das restrições mencionadas no json.
Depois, gere um pegueno texto explicativo com base nessa análise, respondendo:

1. O alimento é seguro para consumo? Seja claro e objetivo (S/N).
2. Quais ingredientes e/ou advertências apresentam algum risco, e com qual restrição eles se relacionam? Liste somente todos os ingredientes 
e/ou advertências que apresentam algum risco para a restrição alimentar do usuário, em ordem de aparição do json.


Responda com um texto explicativo, sem JSON, sem listas, sem tópicos, sem enumeração, apenas um texto corrido. Sua resposta deve ser objetiva e clara.
A resposta gerada será exibida para o usuário final, então seja conciso e direto, sem rodeios. além disso, retorne a resposta no seguinte modelo:

"(Seguro ou Não seguro para consumo).
Motivos: (Motivos que levaram a essa recomendação, descritos no tópico 2, de forma resumida e objetiva)."

lembre-se de utilizar letras maiúsculas em início de frases e minúsculas no restante.
"""

    resposta = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return resposta.text

def analisar_com_ia(resposta: dict):

    resposta_ia = verificar_com_ia(
        resposta
    )

    return {
        "analise_regras": resposta,
        "analise_ia": resposta_ia
    }