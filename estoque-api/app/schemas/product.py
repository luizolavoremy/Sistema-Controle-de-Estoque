from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from decimal import Decimal


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int = 0
    category_id: int

    @field_validator("price")
    @classmethod
    def preco_nao_pode_ser_negativo(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("O preço não pode ser negativo")
        return value

    @field_validator("stock_quantity")
    @classmethod
    def estoque_nao_pode_ser_negativo(cls, value: int) -> int:
        if value < 0:
            raise ValueError("O estoque inicial não pode ser negativo")
        return value


ProductCreate.model_rebuild()


class ProductUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category_id: int
    version: int

    @field_validator("price")
    @classmethod
    def preco_nao_pode_ser_negativo(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("O preço não pode ser negativo")
        return value


ProductUpdate.model_rebuild()


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    category_id: int
    version: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


ProductOut.model_rebuild()
