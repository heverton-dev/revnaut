#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v4.0: CONFIGURATION - Redis + Database + API

Production-ready settings
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# DATABASE CONFIG
# ============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://aidd:password@localhost:5432/aidd_generator"
)

DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_TIMEOUT = 10

# ============================================================================
# REDIS CONFIG
# ============================================================================

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_CACHE_URL = os.getenv("REDIS_CACHE_URL", "redis://localhost:6379/1")

REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True,
    'socket_connect_timeout': 10,
    'socket_keepalive': True,
    'socket_keepalive_options': {
        1: 1,
        2: 3,
        3: 3,
    },
    'connection_pool_kwargs': {
        'max_connections': 50,
    }
}

# ============================================================================
# CELERY CONFIG
# ============================================================================

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_CACHE_URL

CELERY_CONFIG = {
    'broker_url': CELERY_BROKER_URL,
    'result_backend': CELERY_RESULT_BACKEND,
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    'task_track_started': True,
    'task_time_limit': 3600,  # 1 hour
    'task_soft_time_limit': 3300,  # 55 min
    'broker_connection_retry_on_startup': True,
}

# ============================================================================
# CACHE CONFIG
# ============================================================================

CACHE_TTL = {
    'project': 300,  # 5 min
    'metrics': 60,   # 1 min
    'status': 30,    # 30 sec
    'logs': 120,     # 2 min
}

# ============================================================================
# API CONFIG
# ============================================================================

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_WORKERS = int(os.getenv("API_WORKERS", "4"))

# ============================================================================
# LOGGING CONFIG
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# FEATURES
# ============================================================================

FEATURES = {
    'async_processing': True,
    'database_persistence': True,
    'redis_caching': True,
    'metrics_tracking': True,
    'retry_feedback_loops': True,
    'v5_learning_loops': False,  # Coming in v5.0
    'v6_maestro': False,  # Coming in v6.0
}

# ============================================================================
# PERFORMANCE TARGETS
# ============================================================================

PERFORMANCE_TARGETS = {
    'api_latency_p99_ms': 500,  # 500ms P99 latency
    'throughput_projects_per_hour': 200,
    'database_query_timeout_ms': 5000,
    'cache_hit_rate_target': 0.70,  # 70% cache hit rate
    'success_rate_target': 0.95,  # 95% success
}

# ============================================================================
# PRINT CONFIG
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("v4.0 CONFIGURATION")
    print("="*70 + "\n")

    print("DATABASE:")
    print(f"  URL: {DATABASE_URL}")
    print(f"  Pool size: {DB_POOL_SIZE}")
    print(f"  Max overflow: {DB_MAX_OVERFLOW}\n")

    print("REDIS:")
    print(f"  URL: {REDIS_URL}")
    print(f"  Cache URL: {REDIS_CACHE_URL}\n")

    print("CELERY:")
    print(f"  Broker: {CELERY_BROKER_URL}")
    print(f"  Backend: {CELERY_RESULT_BACKEND}\n")

    print("API:")
    print(f"  Host: {API_HOST}:{API_PORT}")
    print(f"  Workers: {API_WORKERS}\n")

    print("FEATURES ENABLED:")
    for feature, enabled in FEATURES.items():
        status = "✅" if enabled else "⏳"
        print(f"  {status} {feature}")

    print("\n" + "="*70 + "\n")
