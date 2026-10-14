import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODELO = "gemini-2.5-flash"

print(MODELO)

def analisar_com_ia_gemini(resposta):

    resposta_ia = verificar_com_ia(
        resposta
    )

    return {
        "analise_regras": resposta,
        "analise_ia": resposta_ia
    }


def verificar_com_ia(resultado_regras):
    prompt = f"""
Você é uma IA que ajuda a revisar uma análise de ingredientes e advertências de rótulos alimentares em relação às restrições alimentares informadas pelo usuário.

Estas são as informações do rótulo do produto extraídas por OCR:

{resultado_regras['texto original da OCR']}

Este foi o JSON gerado pela análise anterior do sistema:

{resultado_regras}

Utilize o texto original do OCR para revisar os ingredientes e as advertências identificados na análise anterior. Considere todos os motivos já listados no JSON e verifique se existem riscos relevantes que não foram identificados anteriormente.

Analise cada ingrediente e advertência separadamente e avalie sua relação com cada uma das restrições alimentares informadas pelo usuário.

Não adicione informações irrelevantes, não invente ingredientes ou advertências e não presuma que uma informação está presente no rótulo quando o texto fornecido não permite confirmar isso. Se houver dúvidas de interpretação, registre-as no campo "incertezas".

Retorne um JSON com exatamente a seguinte estrutura:

{{
    "resultado_final": "não recomendado",
    "motivos": [
        {{
            "ingrediente_com_risco": "nome do ingrediente ou advertência",
            "restricao_relacionada": "nome da restrição"
        }}
    ],
    "possíveis omissões da análise anterior": [
        {{
            "ingrediente_omitido": "nome do ingrediente ou advertência",
            "restricao_relacionada": "nome da restrição"
        }}
    ],
    "incertezas": [
        {{
            "ingrediente_com_incerteza": "nome do ingrediente ou advertência",
            "restricao_relacionada": "nome da restrição",
            "motivo": "explicação da incerteza"
        }}
    ],
    "perguntas para análise": [
        {{
            "1. O alimento é seguro para consumo? Seja claro e objetivo": "SIM/NÃO",
            "2. Quais ingredientes e/ou advertências apresentam algum risco, e com"
            " qual (quais) restrições eles se relacionam? Liste somente todos "
            "os ingredientes e/ou advertências que apresentam algum risco "
            "para a restrição alimentar do usuário, em ordem de aparição do "
            "JSON (ou seja, em ordem de aparição da lista de ingredientes e "
            "de advertências).": "alimentos que estão relacionados às restrições. Se não tiver nenhum, escreva 'nenhum alimento "
            "se relaciona com as restrições do usuário'",
            "3. A análise do JSON gerado pelo sistema (API) deu como resultado "
            "a recomendação correta para o usuário, considerando os ingredientes"
            " e/ou advertências do rótulo do produto em relação à restrição do "
            "usuário? Ele encontrou todos os motivos do porquê o alimento não "
            "é seguro?": "Sim/Não, o resultado "não recomendado/recomendado" está/não está correto. Encontrou/Não encontrou todos os motivos."
        }}
    ]
    "resposta final para o usuário": "mensagem resumida e clara"
}}

Regras para preencher os campos:

1. No campo "resultado_final", utilize exclusivamente um dos seguintes valores:
- "não recomendado": quando houver pelo menos um risco identificado relacionado a uma restrição informada pelo usuário.
- "não foram identificados riscos": quando não houver riscos identificados e as informações disponíveis forem suficientes para essa conclusão.
- "inconclusivo": quando houver dúvidas, contradições ou informações insuficientes que impeçam uma conclusão confiável.

2. No campo "motivos", liste os ingredientes e as advertências que apresentam riscos identificados em relação às restrições informadas, incluindo aqueles já identificados pela análise anterior.

3. No campo "possíveis omissões da análise anterior", liste somente os ingredientes ou advertências relacionados a riscos que aparecem no texto original do OCR, mas não foram identificados como riscos na análise anterior. Não repita aqui os itens já registrados em "motivos".

4. No campo "incertezas", liste os ingredientes ou advertências cuja relação com uma restrição não possa ser determinada com confiança. Explique brevemente o motivo da incerteza.

5. Não confunda a ausência de um ingrediente na lista de ingredientes com uma declaração explícita de ausência no rótulo. Da mesma forma, não descarte automaticamente advertências de possível contaminação cruzada por causa de outra informação aparentemente contraditória. Registre contradições relevantes em "incertezas" e não conclua que o produto é seguro quando elas impedirem uma avaliação confiável.

6. A ausência de riscos identificados não constitui garantia de segurança alimentar. Baseie a conclusão nas informações disponíveis e nas restrições informadas pelo usuário.

7. No campo "resposta final para o usuário", explique a conclusão de forma simples, objetiva e direta, mencionando os riscos relevantes e as incertezas que possam afetar a decisão.

8. Quando não houver itens em uma lista, retorne uma lista vazia: [].

Retorne exclusivamente um JSON válido, sem Markdown, sem blocos de código e sem qualquer texto antes ou depois do objeto JSON. Utilize aspas duplas em todas as chaves e valores textuais. Não inclua comentários nem vírgulas extras.


"""

    resposta = client.models.generate_content(
        model= MODELO,
        contents=prompt
    )

    print(resposta)

    return resposta.text

