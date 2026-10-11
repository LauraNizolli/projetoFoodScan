
from ia import verificar_com_ia

resultado_teste = {
    "texto original da OCR": (
        "Ingredientes: farinha de trigo, água, sal e fermento. "
        "ALÉRGICOS: CONTÉM TRIGO."
    ),
    "restricoes alimentares": ["alergia a trigo"],
    "ingredientes com risco": ["farinha de trigo"],
    "advertencias": ["contém trigo"]
}

print("Enviando análise para o Qwen...\n")

try:
    resposta = verificar_com_ia(resultado_teste)

    print("Resposta recebida:\n")
    print(resposta)

except Exception as erro:
    print("Erro durante o teste:")
    print(type(erro).__name__, erro)
