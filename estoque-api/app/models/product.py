# Este arquivo define a tabela "products" no banco de dados,
# usando classes Python em vez de escrever SQL na mão.

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base


# Toda classe que representa uma tabela herda de "Base"
# (aquele Base que criamos no database.py)
class Product(Base):

    # Nome real da tabela dentro do PostgreSQL
    __tablename__ = "products"

    # id: identificador único de cada produto (a "primary key" / PK)
    # auto-incrementa sozinho (1, 2, 3...)
    id = Column(Integer, primary_key=True, index=True)

    # nome do produto. nullable=False = obrigatório, não pode ficar vazio
    name = Column(String, nullable=False)

    # descrição é opcional (nullable=True = pode ficar vazio)
    description = Column(String, nullable=True)

    # preço com 10 dígitos no total, 2 depois da vírgula (ex: 99999999.99)
    # Numeric em vez de float, porque dinheiro não pode ter erro de arredondamento
    price = Column(Numeric(10, 2), nullable=False)

    # quantidade em estoque, começa em 0 se não for informado
    stock_quantity = Column(Integer, nullable=False, default=0)

    # aponta pro id da tabela "categories" (é a "foreign key" / FK)
    # é assim que criamos o relacionamento entre as duas tabelas
    category_id = Column(Integer, ForeignKey("categories.id"))

    # ==========================================
    # coluna que viabiliza o lock otimista.
    # toda vez que o produto for atualizado, esse número aumenta.
    # isso vai nos ajudar a detectar quando duas pessoas tentam
    # editar o mesmo produto ao mesmo tempo (passo 5 do projeto)
    # ==========================================
    version = Column(Integer, nullable=False, default=0)

    # data/hora de criação, preenchida automaticamente pelo banco
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # data/hora da última atualização, atualizada sozinha a cada mudança
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())