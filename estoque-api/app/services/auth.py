# Este arquivo cuida da criação e leitura do token JWT
# (o "crachá digital" que a pessoa recebe depois de fazer login).

import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import jwt, JWTError

# Carrega as variáveis do arquivo .env pro ambiente do programa
load_dotenv()

# Lê a chave secreta do .env, em vez de deixar escrita direto no código.
# Isso é importante porque esse arquivo .py vai pro GitHub, mas o
# .env NÃO vai (está no .gitignore) -- assim a chave real fica protegida.
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
