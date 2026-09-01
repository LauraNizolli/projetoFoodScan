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

Analise cada ingrediente e separadamente e veja se ele apresenta uma relação com cada uma das restrições mencionadas no json.
Depois, gere um pegueno texto explicativo com base nessa análise, respondendo:

1. O alimento é seguro para consumo?
2. Quais ingredientes apresentam algum risco, e com qual restrição eles se relacionam?
3. A análise anterior encontrou todos os motivos do porquê o alimento não é seguro?

Responda de forma curta, clara e fácil de entender.
"""

    resposta = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    return resposta.text