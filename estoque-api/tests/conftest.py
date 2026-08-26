# Este arquivo é especial pro pytest: qualquer coisa definida aqui
# fica disponível automaticamente pra todos os testes, sem precisar
# importar manualmente em cada arquivo.

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


# "client" é uma FIXTURE -- uma peça reutilizável que os testes
# podem "pedir emprestada". Aqui, ela é um cliente HTTP que conversa
# DIRETO com sua aplicação FastAPI, sem precisar do uvicorn rodando
# de verdade nem de rede de verdade -- é tudo simulado em memória,
# só que é a MESMA aplicação e o MESMO banco de dados de sempre.
@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac