# -*- coding: utf-8 -*-
"""
Vertical Slice: Agente Analítico Conversacional Text-to-SQL (Web & WhatsApp da Diretoria)
Parser determinístico de linguagem natural para SQL OLAP com validação léxica/AST e injeção estrita de RLS.
"""

from __future__ import annotations
import json
import re
import time
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db
from src.core.vector_store import compute_semantic_embedding, cosine_similarity
from src.features.intelligence.superset_embedded import build_superset_rls_clause

FORBIDDEN_KEYWORDS = {
    "drop", "delete", "update", "insert", "alter", "grant", "revoke",
    "truncate", "replace", "exec", "execute", "pragma", "create",
    "vacuum", "attach", "detach", "reindex", "upsert"
}

SENSITIVE_COLUMNS = {
    "password_hash", "signing_secret_encrypted", "secret_key"
}

ANALYTICAL_SCHEMA_DOCS: List[Dict[str, str]] = [
    {
        "id": "schema_deals_revenue",
        "description": "total faturado faturamento total receita total quanto faturou vendas gerais deals",
        "sql": (
            "SELECT 'Total Faturado' AS metrica, "
            "COALESCE(SUM(value), 0.0) AS total_faturamento, "
            "COUNT(*) AS total_deals FROM deals"
        ),
    },
    {
        "id": "schema_deals_regional",
        "description": "regional por time faturamento por regional ranking regional equipes vendas",
        "sql": (
            "SELECT COALESCE(t.name, 'Sem Regional') AS regional, "
            "COALESCE(SUM(d.value), 0.0) AS faturamento, "
            "COUNT(d.id) AS total_pedidos "
            "FROM deals d "
            "LEFT JOIN teams t ON d.team_id = t.id "
            "GROUP BY t.name ORDER BY faturamento DESC"
        ),
    },
    {
        "id": "schema_kp_custody",
        "description": "consignado implantes por lote custodia lotes estoque de implantes keypartners",
        "sql": (
            "SELECT batch_number AS lote, "
            "COALESCE(SUM(quantity), 0) AS total_unidades, "
            "COALESCE(SUM(total_value), 0.0) AS valor_imobilizado "
            "FROM kp_custody_ledger "
            "GROUP BY batch_number ORDER BY total_unidades DESC LIMIT 10"
        ),
    },
    {
        "id": "schema_dentgo_orders",
        "description": "dentgo entregas pedidos express courier motoboy logistica",
        "sql": (
            "SELECT status AS status_entrega, "
            "COUNT(*) AS total_pedidos, "
            "COALESCE(SUM(distance_km), 0.0) AS km_total "
            "FROM dentgo_orders "
            "GROUP BY status ORDER BY total_pedidos DESC"
        ),
    },
    {
        "id": "schema_anvisa_rma",
        "description": "anvisa queixas perda nao-osseointegrado rma tecnovigilancia implante perdido",
        "sql": (
            "SELECT failure_reason AS motivo_reclamado, "
            "COUNT(*) AS total_ocorrencias "
            "FROM anvisa_rma_claims "
            "GROUP BY failure_reason ORDER BY total_ocorrencias DESC"
        ),
    },
]


def ensure_analytical_schema_indexed(account_id: str = "0f14ffff") -> None:
    """Indexa metadados do schema analítico no armazenamento vetorial para recuperação semântica."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        for doc in ANALYTICAL_SCHEMA_DOCS:
            emb_id = f"emb_sql_schema_{account_id}_{doc['id']}"
            cur.execute("SELECT id FROM semantic_embeddings WHERE id = ?", (emb_id,))
            if not cur.fetchone():
                vec = compute_semantic_embedding(doc["description"])
                cur.execute(
                    """
                    INSERT OR IGNORE INTO semantic_embeddings (
                        id, tenant_id, entity_type, entity_id, content_chunk, embedding, metadata_json
                    ) VALUES (?, ?, 'analytical_sql_schema', ?, ?, ?, ?)
                    """,
                    (
                        emb_id,
                        account_id,
                        doc["id"],
                        doc["description"],
                        json.dumps(vec),
                        json.dumps({"sql": doc["sql"]}),
                    ),
                )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


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


def natural_language_to_sql(nl_query: str, account_id: str = "0f14ffff") -> str:
    """
    Mapeia perguntas analíticas em linguagem natural para consultas SQL analíticas sobre o schema do Revnault.
    Suporta deals, contacts, kp_consignment_kits, kp_custody_ledger, kp_surgical_orders, dentgo_orders,
    anvisa_rma_claims, clinical_procedure_margins, kp_surgical_health_scores, erp_fiscal_invoices e tasks.
    Extrai filtros de UF (SP, RJ, MG, PR, RS), agregações (SUM, COUNT, AVG) e cláusulas LIMIT.
    """
    ensure_analytical_schema_indexed(account_id=account_id)
    q = nl_query.lower().strip()

    # 1. Extração de UF
    uf_match = re.search(r"\b(sp|rj|mg|pr|rs)\b", q)
    detected_uf = uf_match.group(1).upper() if uf_match else None
    if not detected_uf:
        if "são paulo" in q or "sao paulo" in q:
            detected_uf = "SP"
        elif "rio de janeiro" in q:
            detected_uf = "RJ"
        elif "minas gerais" in q or "minas" in q:
            detected_uf = "MG"
        elif "paraná" in q or "parana" in q:
            detected_uf = "PR"
        elif "rio grande do sul" in q:
            detected_uf = "RS"

    # 2. Extração de LIMIT
    limit_match = re.search(r"\b(?:top|limite|limit|primeir[oa]s?|as|os)\s+(\d+)\b", q)
    if not limit_match:
        limit_match = re.search(r"\b(\d+)\s+(?:principais|primeir[oa]s?|registros|linhas|itens|tarefas|pedidos)\b", q)
    if not limit_match:
        limit_match = re.search(r"\blimit\s+(\d+)\b", q)
    limit_val = int(limit_match.group(1)) if limit_match else None

    # 3. Extração de Agregação
    has_avg = any(k in q for k in ["média", "medio", "media", "médio", "avg"])
    has_sum = any(k in q for k in ["total", "soma", "somar", "quanto", "faturamento", "receita", "sum"])
    has_count = any(k in q for k in ["quantos", "quantas", "contagem", "quantidade", "número de", "numero de", "count"])

    # 4. Detecção da Tabela Alvo e Construção da Query
    # 4.1 Faturamento por regional (compatibilidade estrita com teste existente)
    if any(k in q for k in ["regional", "por time", "faturamento por regional", "ranking regional"]):
        sql = ANALYTICAL_SCHEMA_DOCS[1]["sql"]
        if limit_val:
            sql += f" LIMIT {limit_val}"
        return sql

    # 4.2 erp_fiscal_invoices (notas fiscais, nfe, faturamento fiscal, danfe, cfop)
    if any(k in q for k in ["fiscal", "nota fiscal", "notas fiscais", "nfe", "danfe", "cfop", "invoices"]):
        lim = limit_val or 15
        if has_sum:
            return f"SELECT cfop, COUNT(*) AS total_notas, COALESCE(SUM(total_invoice_value), 0.0) AS valor_total_faturado FROM erp_fiscal_invoices GROUP BY cfop ORDER BY valor_total_faturado DESC LIMIT {lim}"
        elif has_avg:
            return f"SELECT cfop, COALESCE(AVG(total_invoice_value), 0.0) AS ticket_medio_nfe, COUNT(*) AS total_notas FROM erp_fiscal_invoices GROUP BY cfop LIMIT {lim}"
        elif has_count:
            return "SELECT status AS status_nfe, COUNT(*) AS total_notas FROM erp_fiscal_invoices GROUP BY status"
        else:
            return f"SELECT nfe_number, nfe_series, cfop, recipient_name, total_invoice_value, status, sefaz_protocol, created_at FROM erp_fiscal_invoices ORDER BY created_at DESC LIMIT {lim}"

    # 4.3 clinical_procedure_margins (margem clínica, lucratividade, rentabilidade cirúrgica)
    if any(k in q for k in ["margem", "margens", "lucro", "rentabilidade", "lucratividade", "margin", "cadeira", "custo cirurgico", "procedimento cirurgico"]):
        lim = limit_val or 10
        if has_avg:
            return f"SELECT procedure_name AS procedimento, COALESCE(AVG(net_margin_percent), 0.0) AS margem_media_percent, COALESCE(AVG(net_margin_value), 0.0) AS margem_media_reais FROM clinical_procedure_margins GROUP BY procedure_name ORDER BY margem_media_percent DESC LIMIT {lim}"
        elif has_sum:
            return f"SELECT procedure_name AS procedimento, COALESCE(SUM(gross_revenue), 0.0) AS faturamento_bruto, COALESCE(SUM(net_margin_value), 0.0) AS lucro_liquido_total FROM clinical_procedure_margins GROUP BY procedure_name ORDER BY lucro_liquido_total DESC LIMIT {lim}"
        elif has_count:
            return "SELECT is_low_margin AS alerta_baixa_margem, COUNT(*) AS total_procedimentos FROM clinical_procedure_margins GROUP BY is_low_margin"
        else:
            return f"SELECT procedure_name, gross_revenue, supplies_cost, surgeon_fee, net_margin_value, net_margin_percent FROM clinical_procedure_margins ORDER BY net_margin_percent DESC LIMIT {lim}"

    # 4.4 kp_surgical_health_scores (health score cirúrgico, índice de saúde do parceiro)
    if any(k in q for k in ["health score", "health_score", "hsc", "saude do parceiro", "classificacao cirurgica", "score cirurgico"]):
        lim = limit_val or 10
        if has_avg:
            return "SELECT classification AS faixa_hsc, COALESCE(AVG(hsc_score), 0.0) AS score_medio, COUNT(*) AS total_parceiros FROM kp_surgical_health_scores GROUP BY classification"
        elif has_count:
            return "SELECT classification AS faixa_hsc, COUNT(*) AS total_parceiros FROM kp_surgical_health_scores GROUP BY classification ORDER BY total_parceiros DESC"
        else:
            return f"SELECT partner_name, hsc_score, classification, f_cirurgica, g_consignado, s_atendimento, e_canal FROM kp_surgical_health_scores ORDER BY hsc_score DESC LIMIT {lim}"

    # 4.5 anvisa_rma_claims (tecnovigilância, queixas, perda de implante)
    if any(k in q for k in ["anvisa", "rma", "queixa", "queixas", "falha", "osseointegra", "perda", "reclamac"]):
        lim = limit_val or 15
        if has_count:
            return "SELECT failure_reason AS motivo_reclamado, COUNT(*) AS total_ocorrencias FROM anvisa_rma_claims GROUP BY failure_reason ORDER BY total_ocorrencias DESC"
        return f"SELECT batch_number, failure_reason, patient_age, bone_type, status, quarantine_status FROM anvisa_rma_claims ORDER BY created_at DESC LIMIT {lim}"

    # 4.6 dentgo_orders (entregas express, motoboy, courier, logística)
    if any(k in q for k in ["dentgo", "entrega", "entregas", "courier", "motoboy", "express", "km", "logistica"]):
        lim = limit_val or 15
        if has_sum:
            return "SELECT status AS status_entrega, COUNT(*) AS total_pedidos, COALESCE(SUM(distance_km), 0.0) AS km_total FROM dentgo_orders GROUP BY status ORDER BY total_pedidos DESC"
        elif has_avg:
            return "SELECT status AS status_entrega, COUNT(*) AS total_pedidos, COALESCE(AVG(distance_km), 0.0) AS km_medio FROM dentgo_orders GROUP BY status ORDER BY km_medio DESC"
        elif has_count:
            return "SELECT urgency, COUNT(*) AS total_por_urgencia FROM dentgo_orders GROUP BY urgency ORDER BY total_por_urgencia DESC"
        else:
            return ANALYTICAL_SCHEMA_DOCS[3]["sql"]

    # 4.7 kp_surgical_orders (cirurgias, ordens cirúrgicas, pós-operatório)
    if any(k in q for k in ["cirurgia", "cirurgias", "ordem cirurgica", "ordens cirurgicas", "surgical_order", "paciente"]):
        lim = limit_val or 15
        if has_count:
            return "SELECT status AS status_cirurgia, COUNT(*) AS total_ordens FROM kp_surgical_orders GROUP BY status ORDER BY total_ordens DESC"
        return f"SELECT id, patient_identifier, surgery_date, status, agreement_id FROM kp_surgical_orders ORDER BY surgery_date DESC LIMIT {lim}"

    # 4.8 kp_consignment_kits (caixas, kits cirúrgicos, maletas)
    if any(k in q for k in ["consignment_kit", "kit consignado", "kits consignados", "caixa consignada", "caixas", "maleta", "maletas", "instrumental"]):
        lim = limit_val or 20
        if has_count:
            return "SELECT status, COUNT(*) AS total_kits FROM kp_consignment_kits GROUP BY status ORDER BY total_kits DESC"
        return f"SELECT serial_number, name, qr_code, status, current_agreement_id FROM kp_consignment_kits ORDER BY created_at DESC LIMIT {lim}"

    # 4.9 kp_custody_ledger (custódia, lotes de implantes, estoque consignado)
    if any(k in q for k in ["consignad", "custodia", "custódia", "lote", "lotes", "estoque"]):
        lim = limit_val or 10
        if has_sum:
            return f"SELECT batch_number AS lote, COALESCE(SUM(quantity), 0) AS total_unidades, COALESCE(SUM(total_value), 0.0) AS valor_imobilizado FROM kp_custody_ledger GROUP BY batch_number ORDER BY total_unidades DESC LIMIT {lim}"
        elif has_avg:
            return f"SELECT batch_number AS lote, COALESCE(AVG(unit_value), 0.0) AS valor_medio_unitario, SUM(quantity) AS total_unidades FROM kp_custody_ledger GROUP BY batch_number LIMIT {lim}"
        elif has_count:
            return "SELECT movement_type, COUNT(*) AS total_movimentacoes, COALESCE(SUM(quantity), 0) AS total_pecas FROM kp_custody_ledger GROUP BY movement_type"
        else:
            return ANALYTICAL_SCHEMA_DOCS[2]["sql"]

    # 4.10 tasks (tarefas pendentes, atividades, follow-ups)
    if any(k in q for k in ["tarefa", "tarefas", "task", "tasks", "atividade", "atividades", "pendenc", "follow-up", "followup"]):
        lim = limit_val or 15
        if has_count:
            return f"SELECT priority AS prioridade, COUNT(*) AS total_tarefas FROM tasks GROUP BY priority LIMIT {lim}"
        return f"SELECT title, due_date, assignee, priority, completed FROM tasks ORDER BY created_at DESC LIMIT {lim}"

    # 4.11 Contacts (cirurgiões, dentistas, leads, CRO)
    if any(k in q for k in ["contato", "contatos", "cirurgião", "cirurgioes", "cirurgiões", "dentista", "dentistas", "lead", "leads", "médico", "medico", "cro"]):
        where_parts = []
        if detected_uf:
            where_parts.append(f"(uf = '{detected_uf}' OR cro_uf LIKE '%{detected_uf}%')")
        where_str = f" WHERE {' AND '.join(where_parts)}" if where_parts else ""

        if has_avg:
            return f"SELECT 'Média Score Cirurgiões' AS metrica, COALESCE(AVG(score), 0.0) AS media_score, COUNT(*) AS total_cirurgioes FROM contacts{where_str}"
        elif has_count:
            return f"SELECT 'Total de Cirurgiões Cadastrados' AS metrica, COUNT(*) AS total_contatos FROM contacts{where_str}"
        else:
            lim = limit_val or 20
            return f"SELECT name, email, phone, cro_uf, specialty, score, created_at FROM contacts{where_str} ORDER BY score DESC LIMIT {lim}"

    # 4.12 Deals (faturamento, oportunidades)
    if any(k in q for k in ["deal", "deals", "faturad", "faturamento", "receita", "oportunidade", "venda", "ganho", "ticket"]):
        where_parts = []
        if detected_uf:
            where_parts.append(f"(company LIKE '%{detected_uf}%' OR contact_name LIKE '%{detected_uf}%' OR title LIKE '%{detected_uf}%')")
        where_str = f" WHERE {' AND '.join(where_parts)}" if where_parts else ""

        if has_avg:
            return f"SELECT 'Ticket Médio Deals' AS metrica, COALESCE(AVG(value), 0.0) AS ticket_medio, COUNT(*) AS total_deals FROM deals{where_str}"
        elif has_sum or ("quanto" in q):
            return f"SELECT 'Total Faturado' AS metrica, COALESCE(SUM(value), 0.0) AS total_faturamento, COUNT(*) AS total_deals FROM deals{where_str}"
        elif has_count:
            return f"SELECT 'Total de Oportunidades' AS metrica, COUNT(*) AS total_deals, COALESCE(SUM(value), 0.0) AS total_valor FROM deals{where_str}"
        else:
            lim = limit_val or 15
            return f"SELECT title, value, company, contact_name, priority, created_at FROM deals{where_str} ORDER BY created_at DESC LIMIT {lim}"

    # 5. Recuperação semântica vetorial como fallback inteligente
    query_vec = compute_semantic_embedding(q)
    best_sql = None
    best_sim = 0.0
    for doc in ANALYTICAL_SCHEMA_DOCS:
        sim = cosine_similarity(query_vec, compute_semantic_embedding(doc["description"]))
        if sim > best_sim:
            best_sim = sim
            best_sql = doc["sql"]
    if best_sql and best_sim >= 0.45:
        return best_sql

    lim = limit_val or 15
    return f"SELECT title, value, company, contact_name, created_at FROM deals ORDER BY created_at DESC LIMIT {lim}"


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
        sql_base = natural_language_to_sql(natural_language_query, account_id=account_id)
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
        elif any(tbl in sql_base for tbl in [
            "FROM kp_custody_ledger", "FROM dentgo_orders", "FROM anvisa_rma_claims",
            "FROM kp_consignment_kits", "FROM kp_surgical_orders", "FROM clinical_procedure_margins",
            "FROM kp_surgical_health_scores", "FROM erp_fiscal_invoices"
        ]):
            # Tabelas operacionais indexadas por account_id
            adapted_rls = f"account_id = '{account_id}'" if ("owner_id" in rls_clause or "team_id" in rls_clause) else rls_clause
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
