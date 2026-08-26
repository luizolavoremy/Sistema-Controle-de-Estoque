// Componente de login E cadastro na mesma tela --
// um botão alterna entre os dois modos.

import { useState } from "react";
import { API_URL } from "../api";

// "props" são os "argumentos" que um componente recebe de fora.
// Aqui, o componente pai (App.jsx) vai passar uma função "aoLogar",
// que a gente chama quando o login der certo, avisando o pai
// "ei, o token chegou, aqui está ele".
function AuthForm({ aoLogar }) {
  // Controla se a tela está em modo "login" ou "cadastro"
  const [modoCadastro, setModoCadastro] = useState(false);

  // Cada campo do formulário tem sua própria "caixinha de memória"
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [erro, setErro] = useState("");

  // "async" porque vamos usar "await" pra esperar a resposta da API
  async function handleSubmit(evento) {
    // Impede o comportamento padrão do formulário HTML,
    // que seria recarregar a página inteira ao enviar
    evento.preventDefault();
    setErro("");

    try {
      if (modoCadastro) {
        // Modo cadastro: registra o usuário, depois já faz login
        const respostaCadastro = await fetch(`${API_URL}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, email, password }),
        });

        if (!respostaCadastro.ok) {
          const dadosErro = await respostaCadastro.json();
          throw new Error(dadosErro.detail || "Erro ao cadastrar");
        }
      }

      // Login (roda tanto se acabou de cadastrar, quanto se já estava logando)
      const respostaLogin = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!respostaLogin.ok) {
        const dadosErro = await respostaLogin.json();
        throw new Error(dadosErro.detail || "Email ou senha incorretos");
      }

      const dados = await respostaLogin.json();
      aoLogar(dados.access_token); // avisa o componente pai
    } catch (erroCapturado) {
      setErro(erroCapturado.message);
    }
  }

  return (
    <div style={{ maxWidth: "320px", margin: "40px auto" }}>
      <h2>{modoCadastro ? "Criar conta" : "Entrar"}</h2>

      <form onSubmit={handleSubmit}>
        {modoCadastro && (
          <div>
            <label>Nome:</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
        )}

        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div>
          <label>Senha:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        {erro && <p style={{ color: "red" }}>{erro}</p>}

        <button type="submit">{modoCadastro ? "Cadastrar" : "Entrar"}</button>
      </form>

      <button onClick={() => setModoCadastro(!modoCadastro)}>
        {modoCadastro ? "Já tenho conta" : "Criar uma conta"}
      </button>
    </div>
  );
}

export default AuthForm;