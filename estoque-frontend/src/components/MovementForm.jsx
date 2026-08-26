// Formulário pra registrar uma movimentação de estoque (entrada ou saída).
// Esse é o componente que "sente" o lock otimista na prática --
// se alguém mais mexeu no produto entretanto, aparece um erro 409 aqui.

import { useState } from "react";
import { API_URL } from "../api";

function MovementForm({ token, produto, aoSalvar, aoCancelar }) {
  const [type, setType] = useState("out");
  const [quantity, setQuantity] = useState(1);
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function handleSubmit(evento) {
    evento.preventDefault();
    setErro("");
    setEnviando(true);

    const resposta = await fetch(`${API_URL}/movements/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        product_id: produto.id,
        type,
        quantity: parseInt(quantity),
        version: produto.version,
      }),
    });

    setEnviando(false);

    if (!resposta.ok) {
      const dadosErro = await resposta.json();

      if (resposta.status === 409) {
        setErro(
          "Este produto foi alterado por outra operação enquanto você " +
          "preenchia o formulário (lock otimista). Feche esse formulário, " +
          "recarregue a lista, e tente novamente com os dados atualizados."
        );
      } else {
        setErro(dadosErro.detail || "Erro ao registrar movimentação");
      }
      return;
    }

    aoSalvar();
  }

  return (
    <div style={{ border: "1px solid #ccc", padding: "16px", margin: "16px 0" }}>
      <h3>Movimentar estoque -- {produto.name}</h3>
      <p>Estoque atual: {produto.stock_quantity} (versão {produto.version})</p>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Tipo:</label>
          <select value={type} onChange={(e) => setType(e.target.value)}>
            <option value="out">Saída (venda)</option>
            <option value="in">Entrada (reposição)</option>
          </select>
        </div>

        <div>
          <label>Quantidade:</label>
          <input
            type="number"
            min="1"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            required
          />
        </div>

        {erro && <p style={{ color: "red", maxWidth: "320px" }}>{erro}</p>}

        <button type="submit" disabled={enviando}>
          {enviando ? "Enviando..." : "Confirmar"}
        </button>
        <button type="button" onClick={aoCancelar}>Cancelar</button>
      </form>
    </div>
  );
}

export default MovementForm;
