
from pydantic import BaseModel

class Dados(BaseModel):

    nome_produto: str

    ingredientes: str

    advertencias: str

    restricoes: list[str]
