// Centraliza o endereco da API num lugar so.
// Le da variavel de ambiente VITE_API_URL se ela existir (util pra
// deploy, onde o backend nao estara em localhost); senao, usa
// localhost:8000 como padrao pra desenvolvimento local.
export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
