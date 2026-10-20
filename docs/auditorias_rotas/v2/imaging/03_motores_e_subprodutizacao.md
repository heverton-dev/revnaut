# 03. Motores de Backend e Subprodutização — Rota: imaging (Auditoria v2)

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/imaging/router.py`
- **Fatia de Backend:** `src/features/contracts/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Segmentação Automática por IA** | Recurso implementado no motor | Não exposto na interface do usuário | **Backend suporta modelo de segmentação de mandíbula, tela não ativa** |
| **Renderização Volume Rendering (Raymarching)** | Recurso implementado no motor | Não exposto na interface do usuário | **Shader 3D volumétrico disponível mas desativado por performance** |
