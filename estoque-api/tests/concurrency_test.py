# Este é o teste mais importante do projeto: ele prova que o lock
# otimista realmente impede duas movimentações simultâneas de
# corromper o estoque.

import asyncio
import time
import pytest


async def registrar_e_logar(client) -> str:
    # Função auxiliar: cria um usuário novo (com email único, pra não
    # dar conflito se o teste rodar várias vezes) e faz login,
    # devolvendo o token pronto pra usar.
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
    # ==========================================
    # PREPARAÇÃO: cria categoria, usuário logado, e um produto
    # com 10 unidades em estoque
    # ==========================================
    token = await registrar_e_logar(client)
    headers = {"Authorization": f"Bearer {token}"}

    response_categoria = await client.post(
        "/categories/",
        json={"name": f"Categoria Concorrencia {time.time()}"},
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
    assert produto["version"] == 0  # confirma que começou na versão 0

    # ==========================================
    # O TESTE DE VERDADE: duas movimentações, MESMA versão (0),
    # disparadas ao mesmo tempo com asyncio.gather()
    # ==========================================
    def montar_requisicao_movimento():
        return client.post(
            "/movements/",
            json={
                "product_id": produto["id"],
                "type": "out",
                "quantity": 5,
                "version": 0,  # as DUAS mandam a mesma versão, de propósito
            },
            headers=headers,
        )

    # asyncio.gather() dispara as duas ao mesmo tempo, e só continua
    # depois que as DUAS já terminaram (com sucesso ou erro)
    resposta_1, resposta_2 = await asyncio.gather(
        montar_requisicao_movimento(),
        montar_requisicao_movimento(),
    )

    codigos = sorted([resposta_1.status_code, resposta_2.status_code])

    # ==========================================
    # A PROVA: uma tem que ter dado certo (200),
    # a outra tem que ter sido recusada (409)
    # ==========================================
    assert codigos == [200, 409], (
        f"Esperava uma requisição 200 e outra 409, mas recebi: {codigos}. "
        "Isso significaria que o lock otimista NÃO está funcionando."
    )

    # ==========================================
    # CONFIRMAÇÃO EXTRA: o estoque final precisa refletir
    # SÓ UMA movimentação de saída (10 - 5 = 5), nunca duas (10 - 10 = 0)
    # ==========================================
    response_produto_final = await client.get(f"/products/{produto['id']}")
    assert response_produto_final.json()["stock_quantity"] == 5