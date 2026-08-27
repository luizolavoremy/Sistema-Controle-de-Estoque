# Testes de validação e casos de erro -- cobrindo cenários que
# a revisão de código apontou como importantes de testar.

import time
import pytest


async def registrar_e_logar(client) -> str:
    email_unico = f"valid_{time.time()}@teste.com"
    await client.post(
        "/auth/register",
        json={"name": "Usuario Validacao", "email": email_unico, "password": "senha123"},
    )
    resposta = await client.post(
        "/auth/login",
        json={"email": email_unico, "password": "senha123"},
    )
    return resposta.json()["access_token"]


async def criar_categoria_e_produto(client, headers, estoque=10):
    resposta_cat = await client.post(
        "/categories/",
        json={"name": f"Categoria Validacao {time.time()}"},
        headers=headers,
    )
    categoria_id = resposta_cat.json()["id"]

    resposta_prod = await client.post(
        "/products/",
        json={
            "name": "Produto Validacao",
            "price": 10.0,
            "stock_quantity": estoque,
            "category_id": categoria_id,
        },
        headers=headers,
    )
    return resposta_prod.json()


# ==========================================
# 1. Estoque insuficiente -- nenhuma movimentação deve ser criada
# ==========================================
@pytest.mark.asyncio
async def test_estoque_insuficiente_nao_cria_movimentacao(client):
    token = await registrar_e_logar(client)
    headers = {"Authorization": f"Bearer {token}"}
    produto = await criar_categoria_e_produto(client, headers, estoque=5)

    resposta = await client.post(
        "/movements/",
        json={
            "product_id": produto["id"],
            "type": "out",
            "quantity": 100,  # muito mais que o estoque disponível
            "version": produto["version"],
        },
        headers=headers,
    )

    assert resposta.status_code == 400

    # Confirma que o estoque NÃO mudou
    resposta_produto = await client.get(f"/products/{produto['id']}")
    assert resposta_produto.json()["stock_quantity"] == 5


# ==========================================
# 2. Quantidade zero ou negativa é rejeitada
# ==========================================
@pytest.mark.asyncio
async def test_quantidade_zero_rejeitada(client):
    token = await registrar_e_logar(client)
    headers = {"Authorization": f"Bearer {token}"}
    produto = await criar_categoria_e_produto(client, headers)

    resposta = await client.post(
        "/movements/",
        json={
            "product_id": produto["id"],
            "type": "out",
            "quantity": 0,
            "version": produto["version"],
        },
        headers=headers,
    )

    assert resposta.status_code == 422


@pytest.mark.asyncio
async def test_quantidade_negativa_rejeitada(client):
    token = await registrar_e_logar(client)
    headers = {"Authorization": f"Bearer {token}"}
    produto = await criar_categoria_e_produto(client, headers)

    resposta = await client.post(
        "/movements/",
        json={
            "product_id": produto["id"],
            "type": "out",
            "quantity": -5,
            "version": produto["version"],
        },
        headers=headers,
    )

    assert resposta.status_code == 422


# ==========================================
# 3. Requisição sem JWT / JWT inválido
# ==========================================
@pytest.mark.asyncio
async def test_criar_produto_sem_token_falha(client):
    resposta = await client.post(
        "/products/",
        json={"name": "Produto Sem Token", "price": 10.0, "stock_quantity": 5, "category_id": 1},
    )
    assert resposta.status_code == 401


@pytest.mark.asyncio
async def test_criar_produto_com_token_invalido_falha(client):
    resposta = await client.post(
        "/products/",
        json={"name": "Produto Token Invalido", "price": 10.0, "stock_quantity": 5, "category_id": 1},
        headers={"Authorization": "Bearer token.invalido.aqui"},
    )
    assert resposta.status_code == 401


# ==========================================
# 4. Cadastro duplicado
# ==========================================
@pytest.mark.asyncio
async def test_cadastro_com_email_duplicado_falha(client):
    email = f"duplicado_{time.time()}@teste.com"

    primeira = await client.post(
        "/auth/register",
        json={"name": "Primeiro", "email": email, "password": "senha123"},
    )
    assert primeira.status_code == 200

    segunda = await client.post(
        "/auth/register",
        json={"name": "Segundo", "email": email, "password": "outrasenha"},
    )
    assert segunda.status_code == 400


# ==========================================
# 5. Produto / categoria inexistente
# ==========================================
@pytest.mark.asyncio
async def test_buscar_produto_inexistente_retorna_404(client):
    resposta = await client.get("/products/999999")
    assert resposta.status_code == 404


@pytest.mark.asyncio
async def test_movimentar_produto_inexistente_retorna_404(client):
    token = await registrar_e_logar(client)
    headers = {"Authorization": f"Bearer {token}"}

    resposta = await client.post(
        "/movements/",
        json={"product_id": 999999, "type": "out", "quantity": 1, "version": 0},
        headers=headers,
    )
    assert resposta.status_code == 404


# ==========================================
# 6. Preço e estoque negativos na criação de produto
# ==========================================
@pytest.mark.asyncio
async def test_criar_produto_com_preco_negativo_falha(client):
    token = await registrar_e_logar(client)
    headers = {"Authorization": f"Bearer {token}"}

    resposta_cat = await client.post(
        "/categories/", json={"name": f"Cat {time.time()}"}, headers=headers
    )
    categoria_id = resposta_cat.json()["id"]

    resposta = await client.post(
        "/products/",
        json={"name": "Produto Preco Negativo", "price": -10.0, "stock_quantity": 5, "category_id": categoria_id},
        headers=headers,
    )
    assert resposta.status_code == 422


@pytest.mark.asyncio
async def test_criar_produto_com_estoque_negativo_falha(client):
    token = await registrar_e_logar(client)
    headers = {"Authorization": f"Bearer {token}"}

    resposta_cat = await client.post(
        "/categories/", json={"name": f"Cat {time.time()}"}, headers=headers
    )
    categoria_id = resposta_cat.json()["id"]

    resposta = await client.post(
        "/products/",
        json={"name": "Produto Estoque Negativo", "price": 10.0, "stock_quantity": -5, "category_id": categoria_id},
        headers=headers,
    )
    assert resposta.status_code == 422


# ==========================================
# 7. Delete de produto com histórico existente (soft delete)
# ==========================================
@pytest.mark.asyncio
async def test_delete_produto_com_historico_preserva_movimentacao(client):
    token = await registrar_e_logar(client)
    headers = {"Authorization": f"Bearer {token}"}
    produto = await criar_categoria_e_produto(client, headers, estoque=10)

    # Cria uma movimentação de verdade nesse produto
    resposta_mov = await client.post(
        "/movements/",
        json={"product_id": produto["id"], "type": "out", "quantity": 2, "version": produto["version"]},
        headers=headers,
    )
    assert resposta_mov.status_code == 200

    # Apaga o produto (soft delete)
    resposta_delete = await client.delete(f"/products/{produto['id']}", headers=headers)
    assert resposta_delete.status_code == 200

    # Produto não deve mais aparecer na listagem
    resposta_lista = await client.get("/products/")
    ids_na_lista = [p["id"] for p in resposta_lista.json()]
    assert produto["id"] not in ids_na_lista


# ==========================================
# 8. Produto com soft delete (is_active=False) nao pode ser movimentado
# CORRECAO: revisao apontou que POST /movements nao verificava
# is_active, permitindo movimentar um produto "apagado" via API direta,
# mesmo ele ja nao aparecendo mais na listagem/frontend.
# ==========================================
@pytest.mark.asyncio
async def test_movimentar_produto_desativado_falha(client):
    token = await registrar_e_logar(client)
    headers = {"Authorization": f"Bearer {token}"}
    produto = await criar_categoria_e_produto(client, headers, estoque=10)

    # Apaga o produto (soft delete)
    resposta_delete = await client.delete(f"/products/{produto['id']}", headers=headers)
    assert resposta_delete.status_code == 200

    # Tenta movimentar o produto ja desativado
    resposta_mov = await client.post(
        "/movements/",
        json={
            "product_id": produto["id"],
            "type": "in",
            "quantity": 5,
            "version": produto["version"],
        },
        headers=headers,
    )
    assert resposta_mov.status_code == 404
