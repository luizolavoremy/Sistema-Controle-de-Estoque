# Este arquivo define o formato dos dados usados no cadastro e login.

from pydantic import BaseModel, EmailStr, ConfigDict


# Formato que a pessoa manda pra CRIAR uma conta
class UserRegister(BaseModel):
    name: str
    email: EmailStr  # o Pydantic já confere se parece um email de verdade
    password: str    # a senha "crua", digitada pela pessoa (ainda sem hash)


# Força o Pydantic a "terminar de montar" esse schema imediatamente.
# Sem isso, em algumas versões do Python/Pydantic, o schema fica
# "meio pronto" até a primeira vez que é usado, e quebra bem nessa hora.
UserRegister.model_rebuild()


# Formato que a pessoa manda pra FAZER LOGIN
class UserLogin(BaseModel):
    email: EmailStr
    password: str


UserLogin.model_rebuild()


# Formato que a API devolve depois de um login com sucesso
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Formato de um usuário devolvido pela API (sem a senha, é claro!)
class UserOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)