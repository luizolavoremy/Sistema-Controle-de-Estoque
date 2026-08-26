# Este é o arquivo principal do projeto.
# Por enquanto ele só faz uma coisa: conectar no banco e criar
# as 4 tabelas de verdade, baseado nos models que já escrevemos.
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.database import engine, Base
from app import models  # importa o __init__.py, que traz as 4 tabelas
from app.routers import category, product, auth, movement, demo  # importa os arquivos de rotas
from fastapi.middleware.cors import CORSMiddleware

# Cria as tabelas no PostgreSQL, caso elas ainda não existam.
# Se já existirem, essa linha não faz nada (não duplica, não apaga dado).
Base.metadata.create_all(bind=engine)

# Cria a aplicação FastAPI (o "atendente" que vai receber pedidos)
app = FastAPI(title="Sistema de controle de estoque")

# CORS: autoriza o frontend (rodando em outra porta) a conversar
# com essa API. Sem isso, o navegador bloqueia a comunicação por
# segurança, mesmo que os dois estejam no seu próprio PC.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # endereço do seu frontend
    allow_credentials=True,
    allow_methods=["*"],  # permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # permite qualquer cabeçalho (ex: Authorization)
)

# Conecta cada arquivo de rotas na aplicação principal.
# Sem essas linhas, o FastAPI nem saberia que essas rotas existem.
app.include_router(category.router)
app.include_router(product.router)
app.include_router(auth.router)
app.include_router(movement.router)
app.include_router(demo.router)

# ==========================================
# TRATAMENTO GLOBAL DE ERROS
#
# Isso "intercepta" um tipo específico de erro em QUALQUER rota da
# aplicação, sem precisar repetir try/except em cada uma. Antes disso,
# um erro de "nome duplicado" virava um 500 feio (lembra do começo,
# com a categoria "Eletrônicos"?). Agora vira uma resposta organizada.
# ==========================================
@app.exception_handler(IntegrityError)
def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Esse dado conflita com algo que já existe "
                      "(por exemplo, um nome que precisa ser único)."
        },
    )


# Uma rota simples só pra testar se está tudo funcionando.
# Quando você acessar http://localhost:8000 no navegador,
# essa função roda e devolve essa mensagem.
@app.get("/")
def read_root():
    return {"status": "API rodando", "mensagem": "Bem-vindo ao sistema de estoque"}