# Este arquivo define a tabela "users" no banco de dados.
# É aqui que ficam guardados os usuários que vão poder fazer login.

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):

    __tablename__ = "users"

    # identificador único do usuário
    id = Column(Integer, primary_key=True, index=True)

    # nome do usuário
    name = Column(String, nullable=False)

    # email precisa ser único, porque vai ser usado pra fazer login
    email = Column(String, nullable=False, unique=True)

    # NUNCA guardamos a senha em texto puro.
    # Aqui vai ficar o "hash" da senha (uma versão embaralhada,
    # impossível de reverter). Isso é feito com a lib passlib
    # que já instalamos, quando chegarmos na parte de autenticação.
    hashed_password = Column(String, nullable=False)

    # data/hora em que o usuário foi criado
    created_at = Column(DateTime(timezone=True), server_default=func.now())