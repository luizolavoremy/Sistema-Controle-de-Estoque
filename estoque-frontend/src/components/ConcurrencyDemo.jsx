// Tela de demonstração: dispara o endpoint que simula duas "compras"
// simultâneas no mesmo produto, e mostra visualmente o resultado.

import { useState } from "react";
import { API_URL } from "../api";

function ConcurrencyDemo({ token, produtos }) {
  const [produtoId, setProdutoId] = useState("");
  const [resultado, setResultado] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");

  async function rodarDemo() {
    if (!produtoId) return;

    setCarregando(true);
    setResultado(null);
    setErro("");

    const resposta = await fetch(`${API_URL}/demo/concurrency-test/${produtoId}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });

    setCarregando(false);

    if (!resposta.ok) {
      setErro("Erro ao rodar a demonstração. Confirma que o produto tem estoque.");
      return;
    }

    const dados = await resposta.json();
    setResultado(dados);
  }

  return (
    <div
      style={{
        border: "2px solid #2563eb",
        borderRadius: "10px",
        padding: "20px",
        margin: "24px 0",
        backgroundColor: "white",
      }}
    >
      <h2 style={{ marginTop: 0 }}>🔒 Demonstração: Lock Otimista em Ação</h2>
      <p style={{ color: "#475569" }}>
        Escolhe um produto e clica no botão -- o sistema vai disparar DUAS
        "compras" simultâneas nele, pra provar que o lock otimista impede
        estoque incorreto.
      </p>

      <select value={produtoId} onChange={(e) => setProdutoId(e.target.value)} style={{ maxWidth: "320px" }}>
        <option value="">Selecione um produto...</option>
        {produtos.map((p) => (
          <option key={p.id} value={p.id}>
            {p.name} (estoque: {p.stock_quantity})
          </option>
        ))}
      </select>

      <br />

      <button onClick={rodarDemo} disabled={!produtoId || carregando}>
        {carregando ? "Disparando as duas compras..." : "Rodar Demonstração"}
      </button>

      {erro && <p style={{ color: "#dc2626" }}>{erro}</p>}

      {resultado && (
        <div style={{ marginTop: "20px" }}>
          <h3>{resultado.produto}</h3>
          <p>
            Estoque antes: <strong>{resultado.estoque_antes}</strong> → Estoque depois: <strong>{resultado.estoque_depois}</strong>
          </p>
          <p style={{ color: "#64748b" }}>
            Cada compra tentou levar {resultado.quantidade_tentada_por_compra} unidades
          </p>

          <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
            <div
              style={{
                padding: "16px",
                flex: "1",
                minWidth: "200px",
                borderRadius: "8px",
                backgroundColor: resultado.compra_1.sucesso ? "#dcfce7" : "#fee2e2",
                border: `1px solid ${resultado.compra_1.sucesso ? "#86efac" : "#fca5a5"}`,
              }}
            >
              <strong>{resultado.compra_1.sucesso ? "✅ Compra 1: APROVADA" : "❌ Compra 1: BLOQUEADA"}</strong>
              <p style={{ margin: "8px 0 0 0", fontSize: "0.9rem" }}>{resultado.compra_1.detalhe}</p>
            </div>

            <div
              style={{
                padding: "16px",
                flex: "1",
                minWidth: "200px",
                borderRadius: "8px",
                backgroundColor: resultado.compra_2.sucesso ? "#dcfce7" : "#fee2e2",
                border: `1px solid ${resultado.compra_2.sucesso ? "#86efac" : "#fca5a5"}`,
              }}
            >
              <strong>{resultado.compra_2.sucesso ? "✅ Compra 2: APROVADA" : "❌ Compra 2: BLOQUEADA"}</strong>
              <p style={{ margin: "8px 0 0 0", fontSize: "0.9rem" }}>{resultado.compra_2.detalhe}</p>
            </div>
          </div>

          <p style={{ marginTop: "16px", fontStyle: "italic", color: "#64748b" }}>{resultado.explicacao}</p>
        </div>
      )}
    </div>
  );
}

export default ConcurrencyDemo;
