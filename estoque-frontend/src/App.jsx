// Componente principal da aplicação.
// Busca a lista de produtos e distribui pra quem precisar via props.

import { useState, useEffect } from "react";
import AuthForm from "./components/AuthForm";
import ProductList from "./components/ProductList";
import ConcurrencyDemo from "./components/ConcurrencyDemo";
import { API_URL } from "./api";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [produtos, setProdutos] = useState([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    if (token) {
      buscarProdutos();
    }
  }, [token]);

  async function buscarProdutos() {
    setCarregando(true);
    const resposta = await fetch(`${API_URL}/products/`);
    const dados = await resposta.json();
    setProdutos(dados);
    setCarregando(false);
  }

  function handleLogin(novoToken) {
    localStorage.setItem("token", novoToken);
    setToken(novoToken);
  }

  function handleLogout() {
    localStorage.removeItem("token");
    setToken(null);
  }

  if (!token) {
    return <AuthForm aoLogar={handleLogin} />;
  }

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "2px solid #e2e8f0",
          paddingBottom: "16px",
        }}
      >
        <h1 style={{ margin: 0 }}>📦 Sistema de Controle de Estoque</h1>
        <button onClick={handleLogout} style={{ backgroundColor: "#64748b" }}>
          Sair
        </button>
      </div>

      {carregando ? (
        <p>Carregando produtos...</p>
      ) : (
        <>
          <ProductList token={token} produtos={produtos} aoAtualizarProdutos={buscarProdutos} />
          <ConcurrencyDemo token={token} produtos={produtos} />
        </>
      )}
    </div>
  );
}

export default App;
