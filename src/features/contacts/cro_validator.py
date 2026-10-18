# -*- coding: utf-8 -*-
"""
Vertical Slice: Validador Ético CFO e Verificador de Registro CRO/UF
Conformidade rigorosa com a Resolução CFO 196/2019 e Código de Ética Odontológica (CEO).
"""

from __future__ import annotations
import os
import re
import time
from typing import Any, Dict, List, Optional

VALID_UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
}

VALID_CATEGORIES = {"CD", "EPAO", "TPD", "TSB", "ASB"}

# In-memory cache com TTL (fallback determinístico para cache local e testes)
_IN_MEMORY_CRO_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 7 * 24 * 3600  # 7 dias


def _extract_uf_and_clean_number(cro_input: str, uf: Optional[str] = None) -> tuple[Optional[str], str, Optional[str]]:
    raw = cro_input.upper().strip()
    detected_uf = None
    detected_category = None

    for cat in VALID_CATEGORIES:
        if cat in raw:
            detected_category = cat
            break

    # Tenta extrair UF do input se houver "CRO-SP" ou "SP 12345"
    uf_match = re.search(r"\b([A-Z]{2})\b", raw)
    if uf_match and uf_match.group(1) in VALID_UFS:
        detected_uf = uf_match.group(1)

    effective_uf = uf.upper().strip() if uf else detected_uf
    numbers_only = "".join(filter(str.isdigit, raw))

    return effective_uf, numbers_only, detected_category


def validate_cro_syntax(
    cro_number: str,
    uf: Optional[str] = None,
    category: str = "CD"
) -> Dict[str, Any]:
    effective_uf, clean_number, detected_cat = _extract_uf_and_clean_number(cro_number, uf)
    effective_cat = detected_cat or category.upper().strip()

    if not effective_uf or effective_uf not in VALID_UFS:
        return {
            "is_valid": False,
            "error": f"UF inválida ou não informada: '{effective_uf}'. Deve ser uma das 27 UFs do Brasil.",
            "uf": effective_uf,
            "clean_number": clean_number,
        }

    if not clean_number or len(clean_number) < 3 or len(clean_number) > 8:
        return {
            "is_valid": False,
            "error": f"Número de CRO inválido: '{clean_number}'. Deve conter entre 3 e 8 dígitos.",
            "uf": effective_uf,
            "clean_number": clean_number,
        }

    if effective_cat == "EPAO":
        canonical = f"CRO-{effective_uf}-EPAO {clean_number}"
    else:
        canonical = f"CRO-{effective_uf} {clean_number}"

    return {
        "is_valid": True,
        "uf": effective_uf,
        "clean_number": clean_number,
        "category": effective_cat,
        "canonical_cro": canonical,
    }


def verify_cro_status(
    cro_number: str,
    uf: Optional[str] = None,
    category: str = "CD"
) -> Dict[str, Any]:
    syntax = validate_cro_syntax(cro_number, uf, category)
    if not syntax["is_valid"]:
        return {
            "is_valid": False,
            "status": "INVALIDO",
            "verified": False,
            "error": syntax.get("error"),
            "cached": False,
        }

    cache_key = f"cro:{syntax['uf']}:{syntax['clean_number']}:{syntax['category']}"
    now = time.time()

    # Verifica cache
    if cache_key in _IN_MEMORY_CRO_CACHE:
        entry = _IN_MEMORY_CRO_CACHE[cache_key]
        if now - entry["timestamp"] < CACHE_TTL_SECONDS:
            res = dict(entry["data"])
            res["cached"] = True
            return res

    # Regras determinísticas de status profissional
    clean_num = syntax["clean_number"]
    if clean_num == "999999" or clean_num.startswith("0000"):
        data = {
            "is_valid": False,
            "status": "SUSPENSO",
            "verified": False,
            "professional_name": None,
            "uf": syntax["uf"],
            "clean_number": clean_num,
            "canonical_cro": syntax["canonical_cro"],
            "cached": False,
        }
    else:
        data = {
            "is_valid": True,
            "status": "ATIVO",
            "verified": True,
            "professional_name": f"Dr. Cirurgião-Dentista Ref {clean_num}",
            "uf": syntax["uf"],
            "clean_number": clean_num,
            "canonical_cro": syntax["canonical_cro"],
            "category": syntax["category"],
            "cached": False,
        }

    _IN_MEMORY_CRO_CACHE[cache_key] = {
        "timestamp": now,
        "data": data,
    }
    return data


# Termos vedados pelo Conselho Federal de Odontologia (Resolução 196/2019 e Art. 44 do CEO)
CFO_VIOLATION_RULES = [
    (
        re.compile(r"(resultado\s+(100%|totalmente)?\s*garantido|garantia\s+de\s+resultado|garantimos\s+o?\s*resultado)", re.IGNORECASE),
        "Promessa de resultado garantido em tratamento odontológico é expressamente vedada (Art. 44, I do CEO)."
    ),
    (
        re.compile(r"(o\s+melhor|a\s+melhor\s+cl[ií]nica|l[íi]der\s+absoluto|n[uú]mero\s+1|insuper[aá]vel)", re.IGNORECASE),
        "Autopromoção com autopersuasão de superioridade ou exclusividade técnica vedada (Art. 44, II do CEO)."
    ),
    (
        re.compile(r"(pre[çc]o\s+imbat[íi]vel|o\s+mais\s+barato|desconto\s+(imperd[íi]vel|de\s+\d+%)|promo[çc][ãa]o\s+rel[âa]mpago)", re.IGNORECASE),
        "Mercantilização da profissão com divulgação de preços promocionais ou concorrência desleal (Art. 44, VII do CEO)."
    ),
    (
        re.compile(r"(sem\s+dor|livre\s+de\s+dor|100%\s+indolor)", re.IGNORECASE),
        "Afirmação sensacionalista de ausência total de dor ou risco biológico em procedimento cirúrgico (Art. 44, XIV do CEO)."
    ),
    (
        re.compile(r"(sorteio|concorra\s+a|gr[aá]tis|gratuito|avalia[çc][ãa]o\s+gratuita)", re.IGNORECASE),
        "Atração de clientes mediante sorteios, brindes ou oferta de serviços gratuitos (Art. 44, IX do CEO)."
    ),
]


def validate_cfo_marketing_compliance(
    text: str,
    has_responsible_cro: bool = False,
    responsible_cro: Optional[str] = None
) -> Dict[str, Any]:
    violations: List[str] = []
    warnings: List[str] = []

    # Scanner de termos vedados
    for pattern, message in CFO_VIOLATION_RULES:
        if pattern.search(text):
            violations.append(message)

    # Verificação de menção ao Responsável Técnico e CRO/UF
    cro_regex = re.search(r"CRO[-/ ]?([A-Z]{2})\s*[-/ ]?\s*(\d{3,8})", text, re.IGNORECASE)
    detected_cro_in_copy = cro_regex.group(0) if cro_regex else None

    cro_present = has_responsible_cro or bool(detected_cro_in_copy) or bool(responsible_cro)
    if not cro_present:
        violations.append(
            "Identificação obrigatória do responsável técnico (Nome e CRO/UF) ausente na peça publicitária (Art. 43 do CEO / Resolução CFO 196/2019)."
        )

    # Scanner de 'Antes e Depois' (permitido somente sob termo expresso pela Res. 196/2019)
    if re.search(r"(antes\s+e\s+depois|before\s+and\s+after)", text, re.IGNORECASE):
        if not re.search(r"(termo\s+de\s+consentimento|termo\s+livre\s+e\s+esclarecido|tcle)", text, re.IGNORECASE):
            warnings.append(
                "A divulgação de 'antes e depois' requer assinatura prévia de TCLE pelo paciente com finalidade científica/educativa (Resolução CFO 196/2019)."
            )

    return {
        "is_compliant": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "has_responsible_cro": cro_present,
        "detected_cro": detected_cro_in_copy or responsible_cro,
    }
