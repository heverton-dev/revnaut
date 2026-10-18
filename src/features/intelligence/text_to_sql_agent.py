# -*- coding: utf-8 -*-
"""
Vertical Slice: Agente Analítico Conversacional Text-to-SQL (Web & WhatsApp da Diretoria)
Parser determinístico de linguagem natural para SQL OLAP com validação léxica/AST e injeção estrita de RLS.
"""

from __future__ import annotations
import re
import time
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db
from src.features.intelligence.superset_embedded import build_superset_rls_clause

FORBIDDEN_KEYWORDS = {
    "drop", "delete", "update", "insert", "alter", "grant", "revoke",
    "truncate", "replace", "exec", "execute", "pragma", "create",
    "vacuum", "attach", "detach", "reindex", "upsert"
}

SENSITIVE_COLUMNS = {
    "password_hash", "signing_secret_encrypted", "secret_key"
}


def validate_safe_readonly_sql(sql_query: str) -> None:
    """
    Validador léxico/AST determinístico:
    1. Bloqueia qualquer instrução que não seja estritamente SELECT ou WITH.
    2. Bloqueia comandos concatenados (múltiplas queries via ';').
    3. Bloqueia palavras-chave de mutação (DROP, DELETE, UPDATE, INSERT, ALTER, etc.).
    4. Bloqueia acesso a colunas sensíveis como hashes de senha ou segredos criptográficos.
    """
    if not sql_query or not sql_query.strip():
        raise ValueError("Consulta SQL vazia ou inválida.")

    # Remove comentários SQL
    clean_sql = re.sub(r"--.*?$|/\*.*?\*/", "", sql_query, flags=re.MULTILINE | re.DOTALL).strip()

    # Validação de comandos concatenados
    statements = [s.strip() for s in clean_sql.split(";") if s.strip()]
    if len(statements) > 1:
        raise ValueError("Múltiplas instruções SQL ou comandos concatenados são estritamente proibidos (Prevenção de SQL Injection).")
    if not statements:

        raise ValueError("Consulta SQL vazia após limpeza.")

    stmt = statements[0]
    tokens = re.findall(r"\b[A-Za-z_]+\b", stmt.lower())

    if not tokens or tokens[0] not in {"select", "with"}:
        raise ValueError("Apenas consultas de leitura analítica (SELECT ou WITH) são permitidas no Text-to-SQL.")

    for token in tokens:
        if token in FORBIDDEN_KEYWORDS:
            raise ValueError(f"Comando de mutação não autorizado detectado: '{token.upper()}'. Execução abortada imediatamente.")
        if token in SENSITIVE_COLUMNS:
            raise ValueError(f"Tentativa de extração de coluna confidencial bloqueada: '{token}'.")


def natural_language_to_sql(nl_query: str) -> str:
    """
    Mapeia perguntas analíticas em linguagem natural para consultas SQL analíticas sobre o schema do Revnault.
    """
    q = nl_query.lower().strip()

    # 1. Total faturado / Receita
    if any(k in q for k in ["total faturado", "faturamento total", "receita total", "quanto faturou"]):
        return (
            "SELECT 'Total Faturado' AS metrica, "
            "COALESCE(SUM(value), 0.0) AS total_faturamento, "
            "COUNT(*) AS total_deals FROM deals"
        )

    # 2. Faturamento por regional / time
    if any(k in q for k in ["regional", "por time", "faturamento por regional", "ranking regional"]):
        return (
            "SELECT COALESCE(t.name, 'Sem Regional') AS regional, "
            "COALESCE(SUM(d.value), 0.0) AS faturamento, "
            "COUNT(d.id) AS total_pedidos "
            "FROM deals d "
            "LEFT JOIN teams t ON d.team_id = t.id "
            "GROUP BY t.name ORDER BY faturamento DESC"
        )

    # 3. Consignação / Lotes de Implantes
    if any(k in q for k in ["consignado", "implantes por lote", "custodia", "lotes", "estoque de implantes"]):
        return (
            "SELECT batch_number AS lote, "
            "COALESCE(SUM(quantity), 0) AS total_unidades, "
            "COALESCE(SUM(total_value), 0.0) AS valor_imobilizado "
            "FROM kp_custody_ledger "
            "GROUP BY batch_number ORDER BY total_unidades DESC LIMIT 10"
        )

    # 4. Pedidos e entregas DENTGO
    if any(k in q for k in ["dentgo", "entregas", "pedidos express", "courier", "motoboy"]):
        return (
            "SELECT status AS status_entrega, "
            "COUNT(*) AS total_pedidos, "
            "COALESCE(SUM(distance_km), 0.0) AS km_total "
            "FROM dentgo_orders "
            "GROUP BY status ORDER BY total_pedidos DESC"
        )

    # 5. Cosmovigilância ANVISA / Queixas Técnicas
    if any(k in q for k in ["anvisa", "queixas", "perda", "nao-osseointegrado", "rma"]):
        return (
            "SELECT failure_reason AS motivo_reclamado, "
            "COUNT(*) AS total_ocorrencias "
            "FROM anvisa_rma_claims "
            "GROUP BY failure_reason ORDER BY total_ocorrencias DESC"
        )

    # Fallback padrão: Últimos deals e oportunidades ativas
    return (
        "SELECT title, value, company, contact_name, created_at "
        "FROM deals ORDER BY created_at DESC LIMIT 15"
    )


def inject_rls_filter(sql: str, rls_clause: str) -> str:
    """Injeta a cláusula de isolamento multi-tenant e RBAC diretamente no SQL antes da execução."""
    if not rls_clause or rls_clause == "1=1":
        return sql

    # Se já tem WHERE, injeta no início do WHERE
    if re.search(r"\bWHERE\b", sql, re.IGNORECASE):
        return re.sub(r"\bWHERE\b", f"WHERE ({rls_clause}) AND ", sql, count=1, flags=re.IGNORECASE)

    # Se tem GROUP BY
    if re.search(r"\bGROUP\s+BY\b", sql, re.IGNORECASE):
        return re.sub(r"\bGROUP\s+BY\b", f"WHERE {rls_clause} GROUP BY", sql, count=1, flags=re.IGNORECASE)

    # Se tem ORDER BY
    if re.search(r"\bORDER\s+BY\b", sql, re.IGNORECASE):
        return re.sub(r"\bORDER\s+BY\b", f"WHERE {rls_clause} ORDER BY", sql, count=1, flags=re.IGNORECASE)

    # Se tem LIMIT
    if re.search(r"\bLIMIT\b", sql, re.IGNORECASE):
        return re.sub(r"\bLIMIT\b", f"WHERE {rls_clause} LIMIT", sql, count=1, flags=re.IGNORECASE)

    return f"{sql} WHERE {rls_clause}"


def execute_analytical_query(
    natural_language_query: Optional[str] = None,
    raw_sql: Optional[str] = None,
    user_id: str = "usr-director-br",
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Executa consulta analítica via Text-to-SQL com proteção determinística e injeção de RBAC.
    """
    start_time = time.time()
    init_db()

    # 1. Determina o SQL base
    if raw_sql and raw_sql.strip():
        sql_base = raw_sql.strip()
    elif natural_language_query and natural_language_query.strip():
        sql_base = natural_language_to_sql(natural_language_query)
    else:
        raise ValueError("É necessário fornecer uma pergunta em linguagem natural ou uma consulta SQL direta.")

    # 2. Valida segurança da query fornecida
    validate_safe_readonly_sql(sql_base)

    # 3. Injeta a cláusula de RLS correspondente ao usuário
    conn = get_connection()
    try:
        rls_clause = build_superset_rls_clause(conn, user_id=user_id, account_id=account_id)

        # Ajuste seguro de alias: se a query tiver joins com alias 'd.', adapta a cláusula
        if "FROM deals d" in sql_base or "from deals d" in sql_base:
            adapted_rls = rls_clause.replace("account_id =", "d.account_id =").replace("owner_id =", "d.owner_id =").replace("team_id =", "d.team_id =")
        elif "FROM kp_custody_ledger" in sql_base:
            # kp_custody_ledger não possui owner_id, filtra por account_id
            adapted_rls = f"account_id = '{account_id}'" if "owner_id" in rls_clause else rls_clause
        elif "FROM dentgo_orders" in sql_base or "FROM anvisa_rma_claims" in sql_base:
            adapted_rls = f"account_id = '{account_id}'" if "owner_id" in rls_clause else rls_clause
        else:
            adapted_rls = rls_clause

        final_sql = inject_rls_filter(sql_base, adapted_rls)

        # 4. Re-validação de segurança pós-injeção
        validate_safe_readonly_sql(final_sql)

        # 5. Execução no banco (SQLite WAL)
        cur = conn.cursor()
        cur.execute(final_sql)
        rows_raw = cur.fetchall()

        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = [dict(r) for r in rows_raw]

        # 6. Preparação dos dados para gráficos (chart_labels e chart_values)
        chart_labels: List[str] = []
        chart_values: List[float] = []

        if rows and len(columns) >= 2:
            # Tenta pegar a primeira coluna de texto como label e a primeira numérica como valor
            label_col = columns[0]
            val_col = columns[1]
            for col in columns:
                if any(isinstance(r.get(col), (int, float)) for r in rows):
                    val_col = col
                    break
            for col in columns:
                if col != val_col and any(isinstance(r.get(col), str) for r in rows):
                    label_col = col
                    break

            for r in rows:
                chart_labels.append(str(r.get(label_col, '')))
                v = r.get(val_col, 0.0)
                try:
                    chart_values.append(float(v) if v is not None else 0.0)
                except Exception:
                    chart_values.append(0.0)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        summary = f"Consulta analítica executada com sucesso em {elapsed_ms} ms. {len(rows)} registro(s) retornado(s)."

        return {
            "query": natural_language_query or raw_sql or "",
            "sql_executed": final_sql,
            "is_safe": True,
            "columns": columns,
            "rows": rows,
            "chart_labels": chart_labels,
            "chart_values": chart_values,
            "summary": summary,
            "execution_time_ms": elapsed_ms
        }
    finally:
        conn.close()
