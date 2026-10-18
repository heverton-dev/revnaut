# -*- coding: utf-8 -*-
"""
Vertical Slice: Copiloto RAG de Catálogos Técnicos, Torques e Sequência de Fresagem
Indexação e busca vetorial semântica de precisão para especificações cirúrgicas de implantes e próteses.
"""

from __future__ import annotations
import hashlib
import json
import math
import re
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db


def compute_text_embedding(text: str, dim: int = 256) -> List[float]:
    """
    Gera vetor determinístico normalizado (norma L2 = 1.0) para busca semântica cirúrgica,
    balanceando unigramas técnicos, normalização de sinônimos (ex: broca <-> fresa)
    e n-gramas de caracteres para tolerância ortográfica.
    """
    vec = [0.0] * dim
    clean_text = text.lower().strip()
    clean_text = clean_text.replace("broca", "fresa").replace("brocas", "fresas")
    words = re.findall(r"\b[\w\.\-]+\b", clean_text)

    # 1. Pesos para unigramas técnicos
    for w in words:
        h = int(hashlib.sha256(w.encode("utf-8")).hexdigest()[:8], 16)
        vec[h % dim] += 1.5

    # 2. Bigramas de palavras para contexto sintático
    for i in range(len(words) - 1):
        bg = f"{words[i]}_{words[i+1]}"
        h = int(hashlib.sha256(bg.encode("utf-8")).hexdigest()[:8], 16)
        vec[h % dim] += 1.0

    # 3. 3-gramas de caracteres para flexões morfológicas
    for i in range(len(clean_text) - 2):
        trigram = clean_text[i:i+3]
        h = int(hashlib.sha256(trigram.encode("utf-8")).hexdigest()[:8], 16)
        vec[h % dim] += 0.5

    # Normalização L2
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0.0:
        return [round(x / norm, 5) for x in vec]
    return vec


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calcula similaridade de cosseno entre dois vetores normalizados."""
    if len(v1) != len(v2) or not v1:
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return round(dot_product / (norm_a * norm_b), 4)


def ingest_catalog_chunk(
    source_manual: str,
    page_number: int,
    implant_line: str,
    bone_type: Optional[str],
    content_chunk: str,
    drill_sequence: Optional[List[str]] = None,
    recommended_implant_torque_ncm: Optional[float] = None,
    recommended_prosthetic_torque_ncm: Optional[float] = None,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Ingere fragmento de manual cirúrgico com embedding vetorial na tabela semantic_embeddings.
    """
    init_db()
    chunk_id = f"cat-{uuid.uuid4().hex[:8]}"
    vector = compute_text_embedding(f"{implant_line} {bone_type or ''} {content_chunk}")

    metadata = {
        "source_manual": source_manual,
        "page_number": page_number,
        "implant_line": implant_line,
        "bone_type": bone_type,
        "drill_sequence": drill_sequence or [],
        "recommended_implant_torque_ncm": recommended_implant_torque_ncm,
        "recommended_prosthetic_torque_ncm": recommended_prosthetic_torque_ncm
    }

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO semantic_embeddings (
                id, tenant_id, entity_type, entity_id, content_chunk, embedding, metadata_json
            ) VALUES (?, ?, 'catalog_chunk', ?, ?, ?, ?)
        """, (
            chunk_id, account_id, chunk_id, content_chunk,
            json.dumps(vector), json.dumps(metadata)
        ))
        conn.commit()

        return {
            "status": "INGESTED",
            "chunk_id": chunk_id,
            "vector_dimensions": len(vector),
            "message": f"Chunk {chunk_id} indexado com sucesso no catálogo cirúrgico ({len(vector)} dimensões).",
            "source_manual": source_manual,
            "page_number": page_number,
            "implant_line": implant_line
        }
    finally:
        conn.close()



def query_surgical_catalog(
    query: str,
    bone_type: Optional[str] = None,
    min_similarity: float = 0.70,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Executa busca vetorial semântica nos catálogos cirúrgicos oficiais com zero alucinação.
    """
    init_db()
    query_vector = compute_text_embedding(f"{query} {bone_type or ''}")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, content_chunk, embedding, metadata_json
            FROM semantic_embeddings
            WHERE tenant_id = ? AND entity_type = 'catalog_chunk'
        """, (account_id,))
        rows = cur.fetchall()

        best_match: Optional[Dict[str, Any]] = None
        highest_score = 0.0

        for r in rows:
            try:
                emb = json.loads(r["embedding"])
                sim = cosine_similarity(query_vector, emb)
                if sim > highest_score:
                    highest_score = sim
                    meta = json.loads(r["metadata_json"]) if r["metadata_json"] else {}
                    best_match = {
                        "id": r["id"],
                        "content_chunk": r["content_chunk"],
                        "similarity": sim,
                        "metadata": meta
                    }
            except Exception:
                continue

        if best_match and highest_score >= min_similarity:
            meta = best_match["metadata"]
            source = meta.get("source_manual", "Manual Cirúrgico")
            page = meta.get("page_number", 1)
            content = best_match["content_chunk"]
            answer = f"Conforme o manual oficial '{source}' (Pág. {page}): {content}"

            return {
                "query": query,
                "matched": True,
                "similarity_score": round(highest_score, 4),
                "source_manual": source,
                "page_number": page,
                "implant_line": meta.get("implant_line"),
                "bone_type": meta.get("bone_type"),
                "recommended_implant_torque_ncm": meta.get("recommended_implant_torque_ncm"),
                "recommended_prosthetic_torque_ncm": meta.get("recommended_prosthetic_torque_ncm"),
                "drill_sequence": meta.get("drill_sequence") or [],
                "answer": answer,
                "content_chunk": content
            }

        return {
            "query": query,
            "matched": False,
            "similarity_score": round(highest_score, 4) if highest_score > 0 else 0.0,
            "source_manual": None,
            "page_number": None,
            "implant_line": None,
            "bone_type": None,
            "recommended_implant_torque_ncm": None,
            "recommended_prosthetic_torque_ncm": None,
            "drill_sequence": [],
            "answer": "Nenhuma recomendação técnica oficial encontrada com índice de confiança suficiente no catálogo.",
            "content_chunk": None
        }
    finally:
        conn.close()
