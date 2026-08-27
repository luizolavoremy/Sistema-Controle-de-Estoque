# Frontend - Sistema de Controle de Estoque

Interface web em React (com Vite) para o sistema de controle de estoque, consumindo a API FastAPI do diretorio `estoque-api`.

## Funcionalidades

- Login e cadastro de usuario, com token JWT salvo no navegador
- Listagem de produtos em tabela, com nome, preco, estoque e versao (lock otimista)
- Criacao e edicao de produtos, com categoria selecionavel
- Registro de movimentacao de estoque (entrada/saida), respeitando o lock otimista do backend
- Tela de demonstracao: dispara duas "compras" simultaneas no mesmo produto e mostra visualmente qual foi aprovada e qual foi bloqueada pelo lock otimista

## Estrutura

src/
App.jsx componente principal, dono da lista de produtos
api.js endereco base da API
index.css estilos globais
components/
AuthForm.jsx login e cadastro
ProductList.jsx tabela de produtos
ProductForm.jsx criar/editar produto
MovementForm.jsx movimentacao de estoque
ConcurrencyDemo.jsx demonstracao do lock otimista


## Como rodar

Pre-requisito: o backend (`estoque-api`) precisa estar rodando em `http://localhost:8000` -- veja o README na raiz do projeto.

```bash
npm install
npm run dev
```

A aplicacao abre em `http://localhost:5173`.

## Tecnologias

React, Vite, fetch API nativa (sem biblioteca de requisicao HTTP externa).
