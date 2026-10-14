from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form
)

from executar_ocr import executar_ocr
from extrair_dados_rotulo import extrair_dados_rotulo
from executar_analise import executar_analise
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ==========================
# HOME
# ==========================

@app.get("/")
def home():

    return {
        "Mensagem":
            "FoodScan funcionando!"
    }


# ==========================
# ANÁLISE POR TEXTO
# ==========================

@app.post("/analisar")
def analisar(
    texto_ocr: str = Form(...),
    ingredientes: str = Form(...),
    advertencias: str = Form(...),
    restricoes: str = Form(...)
):


    lista_restricoes = [
            r.strip()
            for r
            in restricoes.split(",")
        ]

    analise = executar_analise(
            
            texto_ocr,
    
            ingredientes,
    
            advertencias,
    
            lista_restricoes
        )

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

# ==========================
# ANÁLISE POR IMAGEM
# ==========================

@app.post("/analisar-imagem")
async def analisar_imagem(

    imagem: UploadFile = File(...),
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
        
        texto_ocr,

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
    # ==========================
    # Terminamosss (????)
    # ==========================