# Este arquivo define o formato dos dados de movimentação de estoque.

from pydantic import BaseModel, ConfigDict, field_validator
from app.models.movement import MovementType


# Formato que a pessoa manda pra registrar uma movimentação
class MovementCreate(BaseModel):
    product_id: int
    type: MovementType       # "in" (entrada) ou "out" (saída)
    quantity: int

    # A versão do produto que a pessoa LEU antes de mandar essa requisição.
    version: int

    @field_validator("quantity")
    @classmethod
    def quantity_deve_ser_positiva(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("A quantidade deve ser maior que zero")
        return value


MovementCreate.model_rebuild()


# Formato que a API devolve depois de registrar a movimentação
class MovementOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    type: MovementType
    quantity: int

    model_config = ConfigDict(from_attributes=True)


MovementOut.model_rebuild()