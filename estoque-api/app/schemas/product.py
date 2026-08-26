# Este arquivo define o "formato" dos dados que entram e saem da API
# pra produtos.

from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal


# Formato pra CRIAR um produto novo.
# Sem "id" e sem "versao" -- os dois são controlados pelo banco/sistema,
# a pessoa que está criando não escolhe esses valores.
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int = 0
    category_id: int


# Força o Pydantic a terminar de montar o schema imediatamente
# (necessário no Python 3.14 por causa de uma mudança em como
# anotações de tipo são avaliadas).
ProductCreate.model_rebuild()


# Formato pra ATUALIZAR um produto.
class ProductUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category_id: int
    version: int


ProductUpdate.model_rebuild()


# Formato que a API DEVOLVE.
class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    category_id: int
    version: int

    model_config = ConfigDict(from_attributes=True)


ProductOut.model_rebuild()