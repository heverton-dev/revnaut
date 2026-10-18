# -*- coding: utf-8 -*-
"""
TDD for [TICKET-03] PostgreSQL 16 + pgvector & Semantic Vector Store
Validates:
- Split async session providers: get_write_db and get_read_db
- Storage of embeddings in semantic_embeddings table
- Mathematical cosine similarity search ranking
- Strict tenant_id isolation in vector searches
"""

import asyncio
import math
import pytest
from sqlalchemy import text
from src.core.database import get_write_db, get_read_db
from src.core.vector_store import VectorStoreService


def test_split_write_read_db_sessions():
    """Garante que get_write_db e get_read_db fornecem sessões assíncronas válidas."""
    async def _run():
        async for w_session in get_write_db():
            assert w_session is not None
            break

        async for r_session in get_read_db():
            assert r_session is not None
            break

    asyncio.run(_run())


def test_semantic_vector_search_ranking_and_tenant_isolation():
    """Insere fragmentos técnicos de catálogos odontológicos e valida ranking semântico e isolamento."""
    async def _run():
        service = VectorStoreService()

        # Garante contas de teste criadas e limpa execuções anteriores
        async for session in get_write_db():
            await session.execute(text(
                "INSERT OR IGNORE INTO accounts (id, name) VALUES ('tenant-alpha', 'Alpha Dental'), ('tenant-beta', 'Beta Dental');"
            ))
            await session.execute(text(
                "DELETE FROM semantic_embeddings WHERE tenant_id IN ('tenant-alpha', 'tenant-beta');"
            ))
            await session.commit()
            break

        # Cria embeddings sintéticos determinísticos de 4 dimensões para teste metrológico
        # Query: "torque de inserção implante cônico" -> vetor alinhado a [1.0, 0.0, 0.0, 0.0]
        v_query = [1.0, 0.0, 0.0, 0.0]

        # Doc 1: Cone Morse torque cônico (alta similaridade) -> [0.95, 0.1, 0.0, 0.0]
        # Doc 2: Hexágono Externo torque intermediário -> [0.6, 0.5, 0.0, 0.0]
        # Doc 3: Resina ortodôntica (baixa similaridade) -> [0.0, 1.0, 0.0, 0.0]
        # Doc 4: Documento do tenant-adversario com alta similaridade -> [0.99, 0.0, 0.0, 0.0]

        await service.store_embedding(
            tenant_id="tenant-alpha",
            entity_type="catalog",
            entity_id="cat-01",
            content_chunk="Implante Cônico Cone Morse: torque recomendado de 35 a 45 N.cm.",
            embedding=[0.95, 0.1, 0.0, 0.0],
            metadata={"system": "Cone Morse"},
        )
        await service.store_embedding(
            tenant_id="tenant-alpha",
            entity_type="catalog",
            entity_id="cat-02",
            content_chunk="Implante Cilíndrico Hexágono Externo: torque de 30 N.cm.",
            embedding=[0.6, 0.5, 0.0, 0.0],
            metadata={"system": "Hexágono Externo"},
        )
        await service.store_embedding(
            tenant_id="tenant-alpha",
            entity_type="catalog",
            entity_id="cat-03",
            content_chunk="Braquete metálico para ortodontia fixa.",
            embedding=[0.0, 1.0, 0.0, 0.0],
            metadata={"system": "Ortodontia"},
        )
        await service.store_embedding(
            tenant_id="tenant-beta",
            entity_type="catalog",
            entity_id="cat-beta",
            content_chunk="Implante Cônico do Concorrente (Confidencial)",
            embedding=[0.99, 0.0, 0.0, 0.0],
            metadata={"system": "Secreto"},
        )

        # Busca pelo tenant-alpha
        results = await service.search_similar(
            tenant_id="tenant-alpha",
            query_embedding=v_query,
            top_k=3,
        )

        assert len(results) == 3
        # O documento mais similar deve ser o Implante Cônico Cone Morse (cat-01)
        assert results[0]["entity_id"] == "cat-01"
        assert "Cone Morse" in results[0]["content_chunk"]
        assert results[0]["similarity"] > results[1]["similarity"]

        # O documento do tenant-beta JAMAIS deve aparecer na busca do tenant-alpha
        entity_ids = [r["entity_id"] for r in results]
        assert "cat-beta" not in entity_ids

    asyncio.run(_run())
