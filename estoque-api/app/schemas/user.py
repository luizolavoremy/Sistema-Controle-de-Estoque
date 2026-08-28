# Este arquivo define o formato dos dados usados no cadastro e login.

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


# bcrypt trabalha com no MAXIMO 72 BYTES (nao 72 caracteres -- um
# emoji ou acento pode ocupar varios bytes em UTF-8). Senha maior
# que isso faz bcrypt.hashpw() estourar ValueError (bcrypt>=4.1),
# e sem essa validacao aqui isso vira um 500 em vez de um 422.
SENHA_MAX_BYTES = 72
SENHA_MIN_CARACTERES = 8


def _validar_senha(v: str) -> str:
    if len(v) < SENHA_MIN_CARACTERES:
        raise ValueError(f"A senha precisa ter pelo menos {SENHA_MIN_CARACTERES} caracteres")
    if len(v.encode("utf-8")) > SENHA_MAX_BYTES:
        raise ValueError(
            f"A senha nao pode ultrapassar {SENHA_MAX_BYTES} bytes "
            "(acentos e emojis contam como mais de 1 byte cada)"
        )
    return v


# Formato que a pessoa manda pra CRIAR uma conta
class UserRegister(BaseModel):
    name: str
    email: EmailStr  # o Pydantic já confere se parece um email de verdade
    password: str    # a senha "crua", digitada pela pessoa (ainda sem hash)

    @field_validator("password")
    @classmethod
    def validar_senha(cls, v: str) -> str:
        return _validar_senha(v)


# Força o Pydantic a "terminar de montar" esse schema imediatamente.
# Sem isso, em algumas versões do Python/Pydantic, o schema fica
# "meio pronto" até a primeira vez que é usado, e quebra bem nessa hora.
UserRegister.model_rebuild()


# Formato que a pessoa manda pra FAZER LOGIN
class UserLogin(BaseModel):
    email: EmailStr
    password: str

    # No login so validamos o limite de bytes (o mesmo bcrypt.checkpw()
    # quebra com ValueError acima de 72 bytes) -- NAO exigimos o minimo
    # de caracteres aqui, pra nao rejeitar por formato uma tentativa de
    # login que deveria simplesmente falhar por credencial invalida.
    @field_validator("password")
    @classmethod
    def validar_tamanho_senha(cls, v: str) -> str:
        if len(v.encode("utf-8")) > SENHA_MAX_BYTES:
            raise ValueError(f"A senha nao pode ultrapassar {SENHA_MAX_BYTES} bytes")
        return v


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
