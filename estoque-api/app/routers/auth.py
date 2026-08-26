# Este arquivo define as rotas de cadastro e login.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, Token, UserOut
from app.services.security import hash_password, verify_password
from app.services.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


# ==========================================
# CADASTRAR um usuário novo
# ==========================================
@router.post("/register", response_model=UserOut)
def register(data: UserRegister, db: Session = Depends(get_db)):
    # Confere se já existe alguém com esse email
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Transforma a senha crua em hash ANTES de salvar no banco
    new_user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ==========================================
# LOGIN -- devolve um token JWT se a senha estiver certa
# ==========================================
@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    # Se o usuário não existe OU a senha não bate, devolvemos
    # o MESMO erro genérico nos dois casos. Isso é de propósito:
    # se dissermos "email não existe" vs "senha errada" separadamente,
    # um invasor consegue descobrir quais emails estão cadastrados.
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    # Gera o token, colocando o id do usuário dentro dele.
    # É assim que, mais pra frente, vamos saber QUEM está fazendo
    # cada requisição, só olhando o token.
    access_token = create_access_token(data={"user_id": user.id})

    return Token(access_token=access_token)