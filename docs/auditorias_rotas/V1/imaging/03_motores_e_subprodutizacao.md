# 03. Motores de Backend e Subprodutização — Rota: imaging

## 1. Motores Subjacentes do Ecossistema
A rota conecta-se diretamente às seguintes fatias verticais do backend:
- **Fatia de Backend:** `src/features/storage/router.py`

---

## 2. Análise de Subprodutização do Motor (Capacidades Ociosas)

| Recurso / Capacidade do Motor | O Que o Backend Executa | O Que a Tela Consome Atualmente | Diagnóstico de Subprodutização & Potencial |
| :--- | :--- | :--- | :--- |
| **Servidor Orthanc PACS** | Recurso implementado no motor | Não exposto na interface do usuário | **Conector PACS implementado no backend, mas UI só aceita upload local de arquivo** |
| **Segmentação Automática por IA** | Recurso implementado no motor | Não exposto na interface do usuário | **Detecção de canal mandibular calculada mas sem toggle na interface** |
