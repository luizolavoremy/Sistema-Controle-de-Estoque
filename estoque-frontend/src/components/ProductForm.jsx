// Formulário pra CRIAR um produto novo, ou EDITAR um existente --
// o mesmo componente serve pros dois casos.

import { useState, useEffect } from "react";
import { API_URL } from "../api";

// "produto" vem preenchido se for edição, ou null se for criação.
// "aoSalvar" é chamado depois de salvar com sucesso, pra avisar
// o componente pai (ProductList) recarregar a lista e fechar o formulário.
function ProductForm({ token, produto, aoSalvar, aoCancelar }) {
  const [categorias, setCategorias] = useState([]);
  const [name, setName] = useState(produto?.name || "");
  const [description, setDescription] = useState(produto?.description || "");
  const [price, setPrice] = useState(produto?.price || "");
  const [stockQuantity, setStockQuantity] = useState(produto?.stock_quantity || 0);
  const [categoryId, setCategoryId] = useState(produto?.category_id || "");
  const [erro, setErro] = useState("");

  const estaEditando = produto !== null;

  // Busca a lista de categorias pra preencher o <select>
  useEffect(() => {
    fetch(`${API_URL}/categories/`)
      .then((r) => r.json())
      .then(setCategorias);
  }, []);

  async function handleSubmit(evento) {
    evento.preventDefault();
    setErro("");

    const corpo = estaEditando
      ? {
          // Ao EDITAR, o backend exige a "version" -- é o lock otimista.
          // Mandamos a versão que já veio junto com o produto carregado.
          name,
          description,
          price: parseFloat(price),
          category_id: parseInt(categoryId),
          version: produto.version,
        }
      : {
          // Ao CRIAR, não existe "version" ainda -- o backend começa em 0
          name,
          description,
          price: parseFloat(price),
          stock_quantity: parseInt(stockQuantity),
          category_id: parseInt(categoryId),
        };

    const url = estaEditando ? `${API_URL}/products/${produto.id}` : `${API_URL}/products/`;
    const metodo = estaEditando ? "PUT" : "POST";

    const resposta = await fetch(url, {
      method: metodo,
      headers: {
        "Content-Type": "application/json",
        // As rotas de criar/editar são PROTEGIDAS -- por isso
        // mandamos o token aqui, igual fizemos manualmente no /docs
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(corpo),
    });

    if (!resposta.ok) {
      const dadosErro = await resposta.json();
      setErro(dadosErro.detail || "Erro ao salvar produto");
      return;
    }

    aoSalvar(); // avisa o pai: "salvei, pode recarregar a lista"
  }

  return (
    <div style={{ border: "1px solid #ccc", padding: "16px", margin: "16px 0" }}>
      <h3>{estaEditando ? "Editar Produto" : "Novo Produto"}</h3>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Nome:</label>
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </div>

        <div>
          <label>Descrição:</label>
          <input value={description} onChange={(e) => setDescription(e.target.value)} />
        </div>

        <div>
          <label>Preço:</label>
          <input
            type="number"
            step="0.01"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
          />
        </div>

        {/* Estoque inicial só faz sentido ao CRIAR --
            depois disso, o estoque só muda via movimentação */}
        {!estaEditando && (
          <div>
            <label>Estoque inicial:</label>
            <input
              type="number"
              value={stockQuantity}
              onChange={(e) => setStockQuantity(e.target.value)}
            />
          </div>
        )}

        <div>
          <label>Categoria:</label>
          <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} required>
            <option value="">Selecione...</option>
            {categorias.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>

        {erro && <p style={{ color: "red" }}>{erro}</p>}

        <button type="submit">Salvar</button>
        <button type="button" onClick={aoCancelar}>Cancelar</button>
      </form>
    </div>
  );
}

export default ProductForm;