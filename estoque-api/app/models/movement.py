# Este arquivo define a tabela "movements" no banco de dados.
# É aqui que fica o HISTÓRICO de toda entrada e saída de estoque.

import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base


# Define os únicos valores que o campo "type" pode ter.
# Isso evita alguém digitar "entrda" errado, ou "compra", ou qualquer
# outra coisa que não seja um desses dois valores.
class MovementType(str, enum.Enum):
    IN = "in"    # entrada de estoque (ex: compra, reposição)
    OUT = "out"  # saída de estoque (ex: venda)


class Movement(Base):

    __tablename__ = "movements"

    # identificador único da movimentação
    id = Column(Integer, primary_key=True, index=True)

    # aponta pro produto que foi movimentado (FK pra tabela products)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # aponta pro usuário que fez a movimentação (FK pra tabela users)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # tipo da movimentação: só pode ser "in" ou "out"
    type = Column(Enum(MovementType), nullable=False)

    # quantidade movimentada (sempre um número positivo,
    # o "type" é que diz se soma ou subtrai do estoque)
    quantity = Column(Integer, nullable=False)

    # data/hora em que a movimentação aconteceu
    created_at = Column(DateTime(timezone=True), server_default=func.now())