import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carrega as variáveis do arquivo .env pro ambiente do programa
load_dotenv()

# Lê o endereço do banco do .env, em vez de deixar escrito direto
# no código. Mesma razão da SECRET_KEY: esse arquivo .py vai pro
# GitHub, mas o .env não vai (está no .gitignore).
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
