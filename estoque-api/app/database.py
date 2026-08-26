from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Endereço do banco: usuário:senha@endereço:porta/nome_do_banco
# Esses valores são os mesmos que usamos no comando docker run
DATABASE_URL = "postgresql://admin:admin123@localhost:5432/estoque"

# "Linha telefônica" entre o Python e o PostgreSQL
engine = create_engine(DATABASE_URL)

# Molde de como cada conversa (sessão) com o banco vai ser aberta
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe mãe de onde todas as tabelas (Produto, Categoria...) vão herdar
Base = declarative_base()


# Função que "empresta" uma conexão com o banco e garante que ela feche depois
def get_db():
    db = SessionLocal()
    try:
        yield db  # empresta a sessão pra quem chamou essa função
    finally:
        db.close()  # fecha a sessão, aconteça o que acontecer