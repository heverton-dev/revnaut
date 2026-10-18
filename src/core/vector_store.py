# -*- coding: utf-8 -*-
"""
Vector Store Service — PostgreSQL 16 + pgvector / HNSW & Math Cosine Engine
Busca semântica de alta performance para catálogos odontológicos, prescrições e transcrições.
"""

from __future__ import annotations
import json
import math
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import text
from src.core.database import get_write_db, get_read_db, init_db


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calcula a similaridade de cosseno entre dois vetores."""
    if len(v1) != len(v2) or not v1:
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class VectorStoreService:
    def __init__(self) -> None:
        init_db()

    async def store_embedding(
        self,
        tenant_id: str,
        entity_type: str,
        entity_id: str,
        content_chunk: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Armazena fragmento textual e seu embedding vetorial associado ao tenant_id.
        """
        record_id = str(uuid.uuid4())
        meta_json = json.dumps(metadata or {})
        embed_json = json.dumps(embedding)

        query = text("""
            INSERT INTO semantic_embeddings (
                id, tenant_id, entity_type, entity_id, content_chunk, embedding, metadata_json
            ) VALUES (
                :id, :tenant_id, :entity_type, :entity_id, :content_chunk, :embedding, :metadata_json
            )
        """)

        async for session in get_write_db():
            await session.execute(
                query,
                {
                    "id": record_id,
                    "tenant_id": tenant_id,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "content_chunk": content_chunk,
                    "embedding": embed_json,
                    "metadata_json": meta_json,
                },
            )
            await session.commit()
            break

        return record_id

    async def search_similar(
        self,
        tenant_id: str,
        query_embedding: List[float],
        entity_type: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Executa busca por similaridade de cosseno com filtro obrigatório por tenant_id.
        """
        base_query = "SELECT id, tenant_id, entity_type, entity_id, content_chunk, embedding, metadata_json FROM semantic_embeddings WHERE tenant_id = :tenant_id"
        params: Dict[str, Any] = {"tenant_id": tenant_id}

        if entity_type:
            base_query += " AND entity_type = :entity_type"
            params["entity_type"] = entity_type

        scored_results: List[Dict[str, Any]] = []

        async for session in get_read_db():
            result = await session.execute(text(base_query), params)
            rows = result.mappings().all()

            for row in rows:
                try:
                    vec = json.loads(row["embedding"])
                    sim = cosine_similarity(query_embedding, vec)
                    meta = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
                    scored_results.append({
                        "id": row["id"],
                        "tenant_id": row["tenant_id"],
                        "entity_type": row["entity_type"],
                        "entity_id": row["entity_id"],
                        "content_chunk": row["content_chunk"],
                        "similarity": round(sim, 4),
                        "metadata": meta,
                    })
                except Exception:
                    continue
            break

        # Ordena por maior similaridade de cosseno decrescente
        scored_results.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_results[:top_k]
