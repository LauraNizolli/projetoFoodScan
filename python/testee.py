from groq_ia import mandar_para_groq

dados_teste = {
    "produto": "Produto fictício",
    "texto original da OCR": (
        "Ingredientes: leite em pó, açúcar e cacau. "
        "ALÉRGICOS: CONTÉM LEITE."
    ),
    "ingredientes": ["leite em pó", "açúcar", "cacau"],
    "advertencias": ["contém leite"],
    "restricoes": ["alergia à proteína do leite"],
    "resultado": "não recomendado",
    "motivos": [
        {
            "ingrediente_com_risco": "leite em pó",
            "restricao_relacionada": "alergia à proteína do leite"
        }
    ]
}

resposta = mandar_para_groq(dados_teste)

print("\nResposta recebida da Groq:")
print(resposta)

print("\nTipo da resposta:", type(resposta))
print("Campos recebidos:", list(resposta.keys()))

