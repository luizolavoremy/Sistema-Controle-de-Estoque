# Testes básicos, só pra confirmar que a API está respondendo certo.

import pytest


# Toda função de teste PRECISA começar com "test_" -- é assim
# que o pytest reconhece o que é um teste e o que não é.
@pytest.mark.asyncio
async def test_rota_raiz_responde(client):
    # "client" aqui é a fixture que criamos no conftest.py --
    # o pytest "injeta" ela automaticamente, só por causa do nome
    # do parâmetro bater com o nome da fixture.
    response = await client.get("/")

    # assert = "eu afirmo que isso é verdade". Se não for,
    # o teste falha e o pytest te mostra exatamente o que esperava
    # vs o que recebeu.
    assert response.status_code == 200
    assert response.json()["status"] == "API rodando"


@pytest.mark.asyncio
async def test_criar_e_listar_categoria(client):
    # Cria uma categoria com um nome único (timestamp no nome
    # evita conflito se você rodar o teste várias vezes)
    import time
    nome_unico = f"Categoria Teste {time.time()}"

    response_criar = await client.post(
        "/categories/",
        json={"name": nome_unico, "description": "Categoria de teste"},
    )
    assert response_criar.status_code == 200
    categoria_criada = response_criar.json()
    assert categoria_criada["name"] == nome_unico

    # Confere que ela aparece na listagem
    response_listar = await client.get("/categories/")
    assert response_listar.status_code == 200
    nomes = [c["name"] for c in response_listar.json()]
    assert nome_unico in nomes