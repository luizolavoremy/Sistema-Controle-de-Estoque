# Este arquivo define a tabela "categories" no banco de dados.

from sqlalchemy import Column, Integer, String
from app.database import Base


class Category(Base):

    __tablename__ = "categories"

    # identificador único da categoria
    id = Column(Integer, primary_key=True, index=True)

    # nome da categoria. unique=True = não pode repetir
    # (ex: não pode existir duas categorias chamadas "Eletrônicos")
    name = Column(String, nullable=False, unique=True)

    # descrição é opcional
    description = Column(String, nullable=True)