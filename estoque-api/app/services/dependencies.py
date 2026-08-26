# Este arquivo define uma "dependência" que qualquer rota protegida
# pode usar. Ela confere o token e devolve o usuário logado --
# ou barra a requisição se o token for inválido/ausente.

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth import decode_access_token

# HTTPBearer é mais simples que OAuth2PasswordBearer: ele só
# espera receber "Authorization: Bearer <token>" -- sem exigir
# um formulário de login dentro do próprio Swagger.
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials  # extrai só o texto do token

    credentials_error = HTTPException(
        status_code=401,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_error

    user_id = payload.get("user_id")
    if user_id is None:
        raise credentials_error

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_error

    return user