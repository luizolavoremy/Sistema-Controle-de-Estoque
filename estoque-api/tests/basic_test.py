# Testes básicos, só pra confirmar que a API está respondendo certo.

import time
import pytest


async def registrar_e_logar(client) -> str:
    # Função auxiliar: cria um usuário novo e faz login, devolvendo
    # o token pronto pra usar em requisições protegidas.
    email_unico = f"basico_{time.time()}@teste.com"

    await client.post(
        "/auth/register",
        json={"name": "Usuario Basico", "email": email_unico, "password": "senha123"},
    )

    response_login = await client.post(
        "/auth/login",
        json={"email": email_unico, "password": "senha123"},
    )
    return response_login.json()["access_token"]


@pytest.mark.asyncio
async def test_rota_raiz_responde(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "API rodando"


@pytest.mark.asyncio
async def test_criar_e_listar_categoria(client):
    # CORREÇÃO: /categories/ agora exige autenticação (item 2 da
    # revisão), então esse teste precisa logar antes de criar.
    token = await registrar_e_logar(client)
    headers = {"Authorization": f"Bearer {token}"}

    nome_unico = f"Categoria Teste {time.time()}"

    response_criar = await client.post(
        "/categories/",
        json={"name": nome_unico, "description": "Categoria de teste"},
        headers=headers,
    )
    assert response_criar.status_code == 200
    categoria_criada = response_criar.json()
    assert categoria_criada["name"] == nome_unico

    # Listar continua ABERTO -- não precisa de token aqui
    response_listar = await client.get("/categories/")
    assert response_listar.status_code == 200
    nomes = [c["name"] for c in response_listar.json()]
    assert nome_unico in nomes
