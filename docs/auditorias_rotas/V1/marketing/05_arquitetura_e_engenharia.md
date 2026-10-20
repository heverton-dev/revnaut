# 05. Arquitetura e Engenharia de Software — Rota: marketing

## 1. Aderência à Arquitetura VSA (Vertical Slice Architecture)
A rota `marketing` implementa uma fatia vertical bem delimitada, encapsulando componentes visuais em `frontend/src/features/campaigns/LandingPageBuilder.tsx` e serviços de backend em fatias autônomas.

---

## 2. Desempenho e Persistência
- Banco de dados em modo SQLite WAL garantindo concorrência limpa sem bloqueio de tabelas.
- Invalidação cirúrgica de cache no React Query para manter a responsividade da aplicação.
