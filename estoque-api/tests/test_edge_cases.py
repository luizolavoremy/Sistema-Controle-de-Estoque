# Testes para os dois bugs de borda encontrados na revisão do
# commit 4646094: demo de concorrência com estoque zero, e senha
# maior que o limite de 72 bytes do bcrypt.

import time
import pytest


async def registrar_e_logar(client, senha="senha123") -> str:
    email_unico = f"teste_{time.time()}@teste.com"

    await client.post(
        "/auth/register",
        json={"name": "Usuário Teste", "email": email_unico, "password": senha},
    )

    response_login = await client.post(
        "/auth/login",
        json={"email": email_unico, "password": senha},
    )
    return response_login.json()["access_token"]


@pytest.mark.asyncio
async def test_demo_concorrencia_rejeita_produto_com_estoque_zero(client):
    # Antes da correção: com estoque 0, max(1, int(0 * 0.6)) == 1,
    # as duas "compras" caíam em "estoque insuficiente" (nunca
    # disputavam o lock de versão), mas o endpoint respondia 200
    # com uma explicação fixa dizendo que "só UMA foi aceita" --
    # falso nesse caso. Agora a demo deve recusar de saída.
    token = await registrar_e_logar(client)
    headers = {"Authorization": f"Bearer {token}"}

    response_categoria = await client.post(
        "/categories/",
        json={"name": f"Categoria Demo Zero {time.time()}"},
        headers=headers,
    )
    categoria_id = response_categoria.json()["id"]

    response_produto = await client.post(
        "/products/",
        json={
            "name": "Produto Sem Estoque",
            "price": 10.0,
            "stock_quantity": 0,
            "category_id": categoria_id,
        },
        headers=headers,
    )
    produto = response_produto.json()

    response_demo = await client.post(
        f"/demo/concurrency-test/{produto['id']}",
        headers=headers,
    )

    assert response_demo.status_code == 400
    assert "estoque" in response_demo.json()["detail"].lower()


@pytest.mark.asyncio
async def test_registro_rejeita_senha_acima_de_72_bytes(client):
    # Antes da correção: bcrypt.hashpw() levanta ValueError pra
    # senhas acima de 72 bytes (bcrypt>=4.1), e isso não era
    # tratado -- virava 500 em vez de 422.
    senha_longa = "a" * 100

    response = await client.post(
        "/auth/register",
        json={
            "name": "Usuário Senha Longa",
            "email": f"senhalonga_{time.time()}@teste.com",
            "password": senha_longa,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_registro_rejeita_senha_curta_demais(client):
    response = await client.post(
        "/auth/register",
        json={
            "name": "Usuário Senha Curta",
            "email": f"senhacurta_{time.time()}@teste.com",
            "password": "123",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_rejeita_senha_acima_de_72_bytes_sem_500(client):
    # Mesmo problema existe em UserLogin, via bcrypt.checkpw().
    # Uma tentativa de login com senha gigante deve virar 422
    # (dado inválido), nunca um 500.
    senha_longa = "b" * 200

    response = await client.post(
        "/auth/login",
        json={"email": "alguem@teste.com", "password": senha_longa},
    )

    assert response.status_code == 422
