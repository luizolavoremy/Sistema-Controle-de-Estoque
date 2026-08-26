# Sistema de Controle de Estoque com Lock Otimista

Sistema full-stack de controle de estoque desenvolvido com FastAPI (backend) e React (frontend), com foco especial em controle de concorrencia real usando lock otimista.

## Destaque tecnico: Lock Otimista

O coracao deste projeto e a prevencao de condicoes de corrida (race conditions) em operacoes de estoque. Quando duas requisicoes tentam modificar o mesmo produto simultaneamente, o sistema garante que apenas uma seja aceita, evitando estoque negativo ou inconsistente.

Como funciona: cada produto possui uma coluna version. Toda atualizacao de estoque exige que o cliente informe a versao que leu. A operacao de escrita no banco combina a checagem de versao e a atualizacao numa unica instrucao atomica (UPDATE ... WHERE id = X AND version = Y), eliminando a brecha de tempo onde a condicao de corrida ocorreria.

Isso e comprovado de duas formas:
- Teste automatizado (tests/concurrency_test.py) que dispara duas requisicoes simultaneas de verdade usando asyncio.gather().
- Endpoint de demonstracao (POST /demo/concurrency-test/{id}) e tela dedicada no frontend, que simulam duas "compras" simultaneas e mostram visualmente qual foi aprovada e qual foi bloqueada.

## Arquitetura

Projeto estoque/
- estoque-api/       Backend (FastAPI + PostgreSQL)
- estoque-frontend/  Frontend (React + Vite)

## Tecnologias

Backend: FastAPI, SQLAlchemy, PostgreSQL (via Docker), JWT (autenticacao), bcrypt (hash de senha), pytest + pytest-asyncio (testes).

Frontend: React, Vite.

## Funcionalidades

- CRUD completo de produtos e categorias
- Autenticacao com JWT (cadastro e login)
- Registro de movimentacoes de estoque (entrada/saida) com lock otimista
- Tratamento de erros consistente (404, 409, 422, etc.)
- Testes automatizados, incluindo teste de concorrencia real
- Interface web completa: login, listagem, CRUD de produtos, movimentacao, e demonstracao visual do lock otimista

## Como rodar o backend

Pre-requisitos: Python 3.11+, Docker Desktop.

docker run --name estoque-db -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin123 -e POSTGRES_DB=estoque -p 5432:5432 -d postgres:16

cd estoque-api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

Cria um arquivo .env com:
SECRET_KEY=sua-chave-secreta-aqui

uvicorn app.main:app --reload

A API estara em http://localhost:8000, com documentacao interativa em http://localhost:8000/docs

## Como rodar o frontend

Pre-requisitos: Node.js.

cd estoque-frontend
npm install
npm run dev

A aplicacao estara em http://localhost:5173

## Rodando os testes

cd estoque-api
pytest

## Autor

Projeto desenvolvido como parte de um estudo pratico de backend, autenticacao, e controle de concorrencia.
