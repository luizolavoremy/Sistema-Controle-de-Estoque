// Componente dedicado a MOSTRAR a lista de produtos e controlar
// os formulários de criar/editar/movimentar. A lista em si agora
// vem de fora (do App.jsx), via prop -- "lifting state up".

import { useState } from "react";
import ProductForm from "./ProductForm";
import MovementForm from "./MovementForm";

function ProductList({ token, produtos, aoAtualizarProdutos }) {
  const [formularioAberto, setFormularioAberto] = useState(null);
  const [movimentandoProduto, setMovimentandoProduto] = useState(null);

  function aoSalvarProduto() {
    setFormularioAberto(null);
    aoAtualizarProdutos(); // pede pro App.jsx recarregar a lista
  }

  function aoSalvarMovimento() {
    setMovimentandoProduto(null);
    aoAtualizarProdutos();
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>Produtos</h2>
        <button onClick={() => setFormularioAberto("novo")}>+ Novo Produto</button>
      </div>

      {formularioAberto && (
        <ProductForm
          token={token}
          produto={formularioAberto === "novo" ? null : formularioAberto}
          aoSalvar={aoSalvarProduto}
          aoCancelar={() => setFormularioAberto(null)}
        />
      )}

      {movimentandoProduto && (
        <MovementForm
          token={token}
          produto={movimentandoProduto}
          aoSalvar={aoSalvarMovimento}
          aoCancelar={() => setMovimentandoProduto(null)}
        />
      )}

      <table border="1" cellPadding="8" style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Descrição</th>
            <th>Preço</th>
            <th>Estoque</th>
            <th>Versão</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {produtos.map((produto) => (
            <tr key={produto.id}>
              <td>{produto.name}</td>
              <td>{produto.description || "--"}</td>
              <td>R$ {produto.price}</td>
              <td>{produto.stock_quantity}</td>
              <td>{produto.version}</td>
              <td>
                <button onClick={() => setFormularioAberto(produto)}>Editar</button>
                {" "}
                <button onClick={() => setMovimentandoProduto(produto)}>Movimentar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ProductList;
