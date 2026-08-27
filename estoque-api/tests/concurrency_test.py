# Este é o teste mais importante do projeto: ele prova que o lock
# otimista realmente impede duas movimentações simultâneas de
# corromper o estoque.

import asyncio
import time
import pytest


async def registrar_e_logar(client) -> str:
    email_unico = f"teste_{time.time()}@teste.com"

    await client.post(
        "/auth/register",
        json={"name": "Usuário Teste", "email": email_unico, "password": "senha123"},
    )

    response_login = await client.post(
        "/auth/login",
        json={"email": email_unico, "password": "senha123"},
    )
    return response_login.json()["access_token"]


@pytest.mark.asyncio
async def test_lock_otimista_impede_dupla_venda_simultanea(client):
    token = await registrar_e_logar(client)
    headers = {"Authorization": f"Bearer {token}"}

    # CORREÇÃO: /categories/ agora exige autenticação (item 2 da
    # revisão) -- precisamos mandar o header aqui também.
    response_categoria = await client.post(
        "/categories/",
        json={"name": f"Categoria Concorrencia {time.time()}"},
        headers=headers,
    )
    categoria_id = response_categoria.json()["id"]

    response_produto = await client.post(
        "/products/",
        json={
            "name": "Produto Teste Concorrencia",
            "price": 10.0,
            "stock_quantity": 10,
            "category_id": categoria_id,
        },
        headers=headers,
    )
    produto = response_produto.json()
    assert produto["version"] == 0

    def montar_requisicao_movimento():
        return client.post(
            "/movements/",
            json={
                "product_id": produto["id"],
                "type": "out",
                "quantity": 5,
                "version": 0,
            },
            headers=headers,
        )

    resposta_1, resposta_2 = await asyncio.gather(
        montar_requisicao_movimento(),
        montar_requisicao_movimento(),
    )

    codigos = sorted([resposta_1.status_code, resposta_2.status_code])

    assert codigos == [200, 409], (
        f"Esperava uma requisição 200 e outra 409, mas recebi: {codigos}. "
        "Isso significaria que o lock otimista NÃO está funcionando."
    )

    response_produto_final = await client.get(f"/products/{produto['id']}")
    assert response_produto_final.json()["stock_quantity"] == 5
