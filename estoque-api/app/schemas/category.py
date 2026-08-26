# Este arquivo define o "formato" dos dados que entram e saem da API
# pra categorias. É diferente do model (que é a tabela do banco).

from pydantic import BaseModel, ConfigDict
from typing import Optional


# Formato que a pessoa precisa mandar pra CRIAR uma categoria.
# Repara que não tem "id" aqui -- quem gera o id é o banco, não a pessoa.
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None  # opcional, pode não vir


CategoryCreate.model_rebuild()


# Formato usado pra ATUALIZAR uma categoria.
class CategoryUpdate(BaseModel):
    name: str
    description: Optional[str] = None


CategoryUpdate.model_rebuild()


# Formato que a API DEVOLVE pra quem pediu.
class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


CategoryOut.model_rebuild()