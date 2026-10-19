# -*- coding: utf-8 -*-
"""
Tests for dynamic natural language to SQL parsing across 11 tables, UF filters, and aggregations.
"""

import pytest
from src.features.intelligence.text_to_sql_agent import (
    natural_language_to_sql,
    execute_analytical_query,
    validate_safe_readonly_sql,
)


def test_text_to_sql_across_all_tables():
    queries = [
        ("Qual a soma total faturada em deals de SP?", "deals", "SUM"),
        ("Quantos contatos de cirurgiões temos no PR?", "contacts", "COUNT"),
        ("Quantos kits consignados temos no total?", "kp_consignment_kits", "COUNT"),
        ("Qual o estoque de implantes consignado por lote?", "kp_custody_ledger", "batch_number"),
        ("Quantas cirurgias agendadas por status?", "kp_surgical_orders", "COUNT"),
        ("Qual a média de km das entregas express do dentgo?", "dentgo_orders", "AVG"),
        ("Quais as queixas de quebra de implante anvisa?", "anvisa_rma_claims", "failure_reason"),
        ("Qual a média de margem de procedimentos cirurgicos?", "clinical_procedure_margins", "AVG"),
        ("Qual a média de health score cirúrgico por faixa?", "kp_surgical_health_scores", "AVG"),
        ("Qual o faturamento total por cfop nas notas fiscais?", "erp_fiscal_invoices", "SUM"),
        ("Quais as 10 principais tarefas comerciais pendentes?", "tasks", "LIMIT 10"),
    ]

    for nl, expected_table, expected_keyword in queries:
        sql = natural_language_to_sql(nl)
        assert expected_table in sql.lower(), f"Tabela {expected_table} esperada na query para: {nl}. Gerado: {sql}"
        assert expected_keyword.lower() in sql.lower(), f"Palavra-chave {expected_keyword} esperada para: {nl}. Gerado: {sql}"
        validate_safe_readonly_sql(sql)


def test_text_to_sql_execution_end_to_end():
    res = execute_analytical_query(
        natural_language_query="Qual a soma do faturamento fiscal por cfop?",
        user_id="usr-sql-director",
        account_id="0f14ffff"
    )
    assert res["is_safe"] is True
    assert "cfop" in res["columns"] or "total_notas" in res["columns"] or "valor_total_faturado" in res["columns"]
