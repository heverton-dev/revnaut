# 🏗️ PLANO ARQUITETURAL: v4.0 → v6.0

**Status:** Planejamento Detalhado  
**Versões:** v4.0 (85/100), v5.0 (95/100), v6.0 (100/100)  
**Timeline:** 14 semanas  
**Investimento:** $51.5k + 340h

---

## 📐 ARQUITETURA GERAL v4.0-v6.0

```
┌─────────────────────────────────────────────────────────────┐
│                      LOAD BALANCER (Nginx)                   │
└──────────┬──────────────────────────────────────────────────┘
           │
    ┌──────┴──────┬──────────┬──────────┐
    │             │          │          │
┌───▼──┐      ┌───▼──┐  ┌───▼──┐  ┌───▼──┐
│ API  │      │ API  │  │ API  │  │ API  │  ← REST API (FastAPI)
│ 8001 │      │ 8002 │  │ 8003 │  │ 8004 │
└───┬──┘      └──┬───┘  └──┬───┘  └──┬───┘
    │            │         │         │
    └────────────┼─────────┼─────────┘
                 │         │
        ┌────────▼────┬────▼───────┐
        │  TASK QUEUE │  CACHE     │
        │  (Redis)    │  (Redis)   │  ← Message Broker + Cache
        └────────┬────┴────┬───────┘
                 │         │
    ┌────────────▼────┬────▼──────────┐
    │                 │               │
┌───▼──────┐    ┌────▼──────┐   ┌────▼──────┐
│ WORKER 1 │    │ WORKER 2  │   │ WORKER 3  │  ← Celery Workers
│ (Async)  │    │ (Async)   │   │ (Async)   │
└───┬──────┘    └────┬──────┘   └────┬──────┘
    │                │               │
    └────────────┬───┴───────────┬───┘
                 │               │
        ┌────────▼───────────────▼────────┐
        │       PostgreSQL Database        │
        │  (Projects, Tasks, Metrics)      │
        └─────────────────────────────────┘
```

---

## 💾 DATABASE SCHEMA (v4.0)

### PostgreSQL Tables

```sql
-- Projetos
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    ideia TEXT NOT NULL,
    status ENUM('queued', 'processing', 'completed', 'failed'),
    score_atual INTEGER,
    score_target INTEGER,
    created_at TIMESTAMP,
    completed_at TIMESTAMP,
    INDEXES: status, created_at
);

-- Tarefas/Phases
CREATE TABLE project_phases (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    phase_number INTEGER,
    phase_name VARCHAR(50),
    status ENUM('pending', 'processing', 'completed', 'failed'),
    gates_passed INTEGER,
    gates_total INTEGER,
    duration_seconds FLOAT,
    tokens_used INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    INDEXES: project_id, status, phase_number
);

-- Erros e Logs
CREATE TABLE phase_logs (
    id UUID PRIMARY KEY,
    phase_id UUID REFERENCES project_phases(id),
    timestamp TIMESTAMP,
    level ENUM('INFO', 'WARNING', 'ERROR'),
    message TEXT,
    stacktrace TEXT,
    INDEXES: phase_id, timestamp, level
);

-- Histórico de Tentativas (Retry)
CREATE TABLE retry_history (
    id UUID PRIMARY KEY,
    phase_id UUID REFERENCES project_phases(id),
    attempt_number INTEGER,
    strategy VARCHAR(50),  -- 'retry', 'context_reduced', 'with_examples', 'escalate'
    status ENUM('success', 'failed'),
    duration_seconds FLOAT,
    error_message TEXT,
    created_at TIMESTAMP,
    INDEXES: phase_id, created_at
);

-- Métricas e Performance
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    metric_name VARCHAR(100),
    metric_value FLOAT,
    tags JSONB,  -- {'model': 'haiku', 'phase': '3', ...}
    recorded_at TIMESTAMP,
    INDEXES: project_id, metric_name, recorded_at
);

-- A/B Testing (v5.0)
CREATE TABLE prompt_experiments (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    prompt_version_a TEXT,
    prompt_version_b TEXT,
    score_a FLOAT,
    score_b FLOAT,
    winner VARCHAR(1),  -- 'A' ou 'B'
    created_at TIMESTAMP,
    INDEXES: project_id, winner
);
```

---

## ⚡ ASYNC STRATEGY (v4.0)

### Tech Stack
- **Message Broker:** Redis (Pub/Sub + Queue)
- **Task Queue:** Celery + Flower (monitoring)
- **Async Framework:** FastAPI + AsyncIO
- **Cache:** Redis (Key-Value)

### Worker Architecture

```python
# File: workers/celery_app.py
from celery import Celery
from redis import Redis

app = Celery(
    'aidd_project_generator',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,  # Monitorar progresso
    task_time_limit=3600,     # Max 1 hora por task
    task_soft_time_limit=3300, # Aviso em 55min
)

# Task: Executar project completo
@app.task(bind=True, name='run_orquestrador')
def run_orquestrador_async(self, project_id, ideia):
    """Task assíncrona que executa orquestrador completo"""
    try:
        # Atualizar status
        project = Project.get(project_id)
        project.status = 'processing'
        project.worker_id = self.request.hostname
        project.save()
        
        # Executar phases
        for phase_num in range(1, 8):
            self.update_state(
                state='PROGRESS',
                meta={
                    'phase': phase_num,
                    'progress': (phase_num / 7) * 100
                }
            )
            
            resultado_phase = executar_phase(project_id, phase_num)
            
            if not resultado_phase['sucesso']:
                project.status = 'failed'
                project.save()
                return {'status': 'failed', 'phase': phase_num}
        
        # Sucesso
        project.status = 'completed'
        project.score_atual = 75  # Exemplo
        project.completed_at = datetime.now()
        project.save()
        
        return {'status': 'completed', 'score': 75}
        
    except Exception as e:
        project.status = 'failed'
        project.error_message = str(e)
        project.save()
        raise

# Task: Self-correction (retry)
@app.task(bind=True, name='retry_phase')
def retry_phase_async(self, phase_id, strategy):
    """Retry com feedback loop"""
    phase = ProjectPhase.get(phase_id)
    fb = FeedbackLoop(max_attempts=3)
    
    resultado = fb.executar_com_retry(
        lambda: executar_phase_com_estrategia(phase_id, strategy),
        task_name=f"Retry {phase_id} com {strategy}"
    )
    
    return resultado
```

### REST API Endpoints (v4.0)

```python
# File: api/routes.py
from fastapi import FastAPI, BackgroundTasks
from celery.result import AsyncResult

app = FastAPI(title="AIDD Project Generator v4.0")

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.post("/projects/generate")
async def generate_project(request: ProjectRequest):
    """
    Gera projeto de forma assíncrona
    
    POST /projects/generate
    {
        "ideia": "Cria um CLI Python que...",
        "opcoes": { "model": "haiku", "profundidade": "completa" }
    }
    
    Response:
    {
        "project_id": "uuid-aqui",
        "status": "queued",
        "task_url": "/tasks/uuid-aqui"
    }
    """
    
    # Criar projeto no DB
    project = Project(
        id=str(uuid4()),
        ideia=request.ideia,
        status='queued'
    )
    project.save()
    
    # Enfileirar task
    task = run_orquestrador_async.delay(project.id, request.ideia)
    project.celery_task_id = task.id
    project.save()
    
    return {
        'project_id': project.id,
        'status': 'queued',
        'task_id': task.id,
        'status_url': f'/projects/{project.id}',
        'task_url': f'/tasks/{task.id}'
    }


@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    """
    GET /projects/{project_id}
    
    Response:
    {
        "id": "uuid",
        "status": "processing",
        "score": 75,
        "progress": 42,  # em %
        "phases": [
            {"numero": 1, "status": "completed", "gates": "4/4"},
            {"numero": 2, "status": "processing", "gates": "2/4"},
            ...
        ]
    }
    """
    
    project = Project.get(project_id)
    if not project:
        return {'error': 'Not found'}, 404
    
    # Pegar task status
    task = AsyncResult(project.celery_task_id)
    progress = 0
    if task.state == 'PROGRESS':
        progress = task.info.get('progress', 0)
    
    # Pegar phases
    phases = ProjectPhase.find(project_id=project_id)
    
    return {
        'id': project.id,
        'ideia': project.ideia,
        'status': project.status,
        'score': project.score_atual,
        'progress': progress,
        'phases': [
            {
                'numero': p.phase_number,
                'nome': p.phase_name,
                'status': p.status,
                'gates': f"{p.gates_passed}/{p.gates_total}",
                'tokens': p.tokens_used,
                'duracao': p.duration_seconds
            }
            for p in phases
        ],
        'criado_em': project.created_at,
        'completado_em': project.completed_at
    }


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    GET /tasks/{task_id}
    
    Monitorar status de uma task em execução
    """
    
    task = AsyncResult(task_id)
    
    response = {
        'task_id': task_id,
        'status': task.state,
        'result': None
    }
    
    if task.state == 'PENDING':
        response['status_mensagem'] = 'Task aguardando na fila'
    elif task.state == 'PROGRESS':
        response['progress'] = task.info.get('progress')
        response['phase'] = task.info.get('phase')
        response['status_mensagem'] = f"Fase {task.info.get('phase')}/7 em progresso"
    elif task.state == 'SUCCESS':
        response['result'] = task.result
        response['status_mensagem'] = 'Projeto gerado com sucesso'
    elif task.state == 'FAILURE':
        response['error'] = str(task.info)
        response['status_mensagem'] = 'Erro na geração'
    
    return response


@app.get("/projects/{project_id}/logs")
async def get_project_logs(project_id: str, level: str = None):
    """
    GET /projects/{project_id}/logs?level=ERROR
    
    Buscar logs de todas as phases
    """
    
    phases = ProjectPhase.find(project_id=project_id)
    all_logs = []
    
    for phase in phases:
        query = PhaseLog.find(phase_id=phase.id)
        
        if level:
            query = query.filter(level=level)
        
        logs = query.order_by('-timestamp').limit(100)
        
        all_logs.extend([
            {
                'fase': phase.phase_number,
                'nivel': log.level,
                'mensagem': log.message,
                'timestamp': log.timestamp,
                'stacktrace': log.stacktrace if log.level == 'ERROR' else None
            }
            for log in logs
        ])
    
    return {
        'project_id': project_id,
        'total_logs': len(all_logs),
        'logs': sorted(all_logs, key=lambda x: x['timestamp'], reverse=True)
    }


@app.get("/metrics")
async def get_system_metrics():
    """
    GET /metrics
    
    Métricas de sistema (para Prometheus/Grafana)
    """
    
    # Contar projetos por status
    projects_by_status = {}
    for status in ['queued', 'processing', 'completed', 'failed']:
        projects_by_status[status] = Project.count(status=status)
    
    # Performance médio
    avg_duration = ProjectPhase.avg('duration_seconds')
    avg_tokens = ProjectPhase.avg('tokens_used')
    
    # Taxa de sucesso
    completed = Project.count(status='completed')
    failed = Project.count(status='failed')
    success_rate = completed / (completed + failed) if (completed + failed) > 0 else 0
    
    return {
        'projetos': projects_by_status,
        'performance': {
            'duracao_media_seconds': avg_duration,
            'tokens_media': avg_tokens,
            'taxa_sucesso': f"{success_rate:.1%}"
        },
        'workers': {
            'ativos': celery_app.control.inspect().active(),
            'registrados': celery_app.control.inspect().registered()
        }
    }


@app.post("/projects/{project_id}/cancel")
async def cancel_project(project_id: str):
    """
    POST /projects/{project_id}/cancel
    
    Cancelar projeto em execução
    """
    
    project = Project.get(project_id)
    if not project:
        return {'error': 'Not found'}, 404
    
    if project.status in ['completed', 'failed', 'cancelled']:
        return {'error': 'Project already finished'}, 400
    
    # Revogar task
    AsyncResult(project.celery_task_id).revoke(terminate=True)
    
    project.status = 'cancelled'
    project.cancelled_at = datetime.now()
    project.save()
    
    return {'status': 'cancelled'}
```

---

## 📈 SCALING PLAN (v4.0)

### Horizontal Scaling Strategy

```yaml
# docker-compose.yml - Exemplo para 3 workers

version: '3.9'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: aidd_generator
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - postgres
    environment:
      REDIS_URL: redis://redis:6379/0
      DATABASE_URL: postgresql://postgres:secure_password@postgres:5432/aidd_generator
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '1'
          memory: 512M

  worker:
    build: .
    command: celery -A workers.celery_app worker --loglevel=info --concurrency=4
    depends_on:
      - redis
      - postgres
    environment:
      REDIS_URL: redis://redis:6379/0
      DATABASE_URL: postgresql://postgres:secure_password@postgres:5432/aidd_generator
    deploy:
      replicas: 3  # 3 workers em paralelo
      resources:
        limits:
          cpus: '2'
          memory: 1G

  flower:
    build: .
    command: celery -A workers.celery_app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api

volumes:
  redis_data:
  postgres_data:
```

### Load Balancing Config

```nginx
# nginx.conf
upstream api_backend {
    server api:8000;
    server api:8001;
    server api:8002;
    server api:8003;
}

server {
    listen 80;
    server_name api.aidd-generator.local;

    location / {
        proxy_pass http://api_backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Connection pooling
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
}
```

### Scaling Metrics

```
Métrica               | v4.0 Start | v4.0 End | v4.0 Goal
─────────────────────┼────────────┼──────────┼──────────
Requests/sec         | 10         | 100      | 200+
Latência P99         | 2s         | 0.5s     | 0.3s
Throughput (proj/h)  | 20         | 200      | 400+
Database connections | 10         | 50       | 100+
Cache hit rate       | 0%         | 70%      | 80%+
Worker utilization   | 50%        | 80%      | 85%+
```

---

## 🧠 LEARNING LOOPS STRATEGY (v5.0)

### A/B Testing Framework

```python
# File: learning/prompt_optimizer.py

class PromptOptimizer:
    """A/B testing automático de prompts"""
    
    def __init__(self):
        self.prompt_versions = {}  # {phase_id: [v1, v1.1, v1.2]}
        self.results = []
    
    def a_b_test(self, prompt_a, prompt_b, n_runs=10):
        """
        A/B teste de 2 prompts
        
        Executa cada um n_runs vezes e usa teste estatístico (t-test)
        para determinar winner com 95% confiança
        """
        
        results_a = []
        results_b = []
        
        for run in range(n_runs):
            # Executar prompt A
            resp_a = agent.run(prompt_a)
            score_a = validate_response(resp_a)
            results_a.append(score_a)
            
            # Executar prompt B
            resp_b = agent.run(prompt_b)
            score_b = validate_response(resp_b)
            results_b.append(score_b)
        
        # Teste T (statistical significance)
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(results_a, results_b)
        
        winner = 'A' if np.mean(results_a) > np.mean(results_b) else 'B'
        significance = 'yes' if p_value < 0.05 else 'no'
        
        return {
            'prompt_a_score': np.mean(results_a),
            'prompt_b_score': np.mean(results_b),
            'winner': winner,
            'p_value': p_value,
            'statistically_significant': significance
        }
    
    def learning_loop(self, n_iterations=50):
        """
        Loop de aprendizado: 50 iterações de A/B testes
        
        Iteração 1: teste v1 vs v1.1
        Iteração 2: teste winner vs v1.2
        Iteração 3: teste new_winner vs v1.3
        ...
        
        Resultado: prompt otimizado para este domínio
        """
        
        current_best = PROMPT_TEMPLATES['phase_2']
        
        for iteration in range(n_iterations):
            # Gerar candidate (pequena variação)
            candidate = self._generate_variant(current_best)
            
            # A/B test
            result = self.a_b_test(current_best, candidate, n_runs=5)
            
            # Atualizar winner
            if result['winner'] == 'B':
                current_best = candidate
                print(f"✅ Iteração {iteration}: Novo winner encontrado! Score: {result['prompt_b_score']:.2f}")
            else:
                print(f"⏸️  Iteração {iteration}: Current best mantém (score: {result['prompt_a_score']:.2f})")
        
        return current_best
    
    def _generate_variant(self, prompt):
        """Gerar variação pequena do prompt"""
        variants = [
            lambda p: p + " Seja bem-vindo.",
            lambda p: p + " Explique suas decisões.",
            lambda p: p + " Use exemplos quando necessário.",
            lambda p: p.replace(".", ". Seja conciso."),
        ]
        return random.choice(variants)(prompt)
```

### Domain-Specific Adaptation (v5.0)

```python
# File: learning/domain_adapter.py

DOMAIN_TEMPLATES = {
    'python': """
        Você é um expert em Python com 10+ anos de experiência.
        
        Ao analisar esta ideia de projeto Python:
        1. Considere as best practices (PEP 8, type hints, testing)
        2. Recomende bibliotecas relevantes (numpy, pandas, fastapi, etc)
        3. Aponte problemas de performance/segurança
        4. Sugira arquitetura escalável
        
        Ideia: {ideia}
    """,
    
    'devops': """
        Você é um especialista em DevOps/Infrastructure com especialidade em:
        - Kubernetes, Docker, Terraform
        - CI/CD pipelines (GitHub Actions, GitLab CI)
        - Monitoring (Prometheus, Grafana)
        - IaC best practices
        
        Ao analisar esta ideia de projeto DevOps:
        1. Defina infraestrutura necessária
        2. Recomende ferramentas apropriadas
        3. Proponha pipeline CI/CD
        4. Inclua estratégia de monitoramento
        
        Ideia: {ideia}
    """,
    
    'web': """
        Você é um expert em desenvolvimento web (Frontend + Backend).
        Stack: React, TypeScript, Node.js, PostgreSQL
        
        Ao analisar esta ideia de projeto web:
        1. Defina arquitetura frontend/backend
        2. Recomende componentes React reutilizáveis
        3. Defina API REST endpoints
        4. Proponha database schema
        
        Ideia: {ideia}
    """
}

class DomainAdapter:
    """Adaptar prompts por domínio de projeto"""
    
    @staticmethod
    def detect_domain(ideia: str) -> str:
        """Detectar domínio da ideia usando keywords"""
        
        keywords = {
            'python': ['python', 'cli', 'script', 'data', 'ml', 'automation'],
            'devops': ['kubernetes', 'docker', 'infra', 'devops', 'ci/cd', 'terraform'],
            'web': ['web', 'frontend', 'backend', 'react', 'api', 'webapp'],
        }
        
        ideia_lower = ideia.lower()
        
        scores = {}
        for domain, kw_list in keywords.items():
            scores[domain] = sum(1 for kw in kw_list if kw in ideia_lower)
        
        return max(scores, key=scores.get) or 'python'
    
    @staticmethod
    def adapt_prompt(ideia: str, base_prompt: str) -> str:
        """Adaptar prompt ao domínio detectado"""
        
        domain = DomainAdapter.detect_domain(ideia)
        domain_prefix = DOMAIN_TEMPLATES.get(domain, "")
        
        return domain_prefix + "\n\n" + base_prompt
```

---

## 🏆 MAESTRO AGÊNTICO ARCHITECTURE (v6.0)

### Autonomous Decision Making

```python
# File: maestro/decision_engine.py

class DecisionEngine:
    """Motor de decisão autônomo (v6.0)"""
    
    def __init__(self):
        self.decision_history = []
        self.learned_patterns = {}
    
    def decide(self, options: List[str], context: Dict, confidence_threshold=0.85):
        """
        Tomar decisão autonomamente
        
        Args:
            options: ["Option A", "Option B", "Option C"]
            context: histórico de decisões similares
            confidence_threshold: mínimo para decidir sem humano
        
        Retorna:
            {
                'escolhida': 'Option B',
                'confianca': 0.92,
                'reasoning': 'Option B funcionou em 8/10 casos similares',
                'escalada_para_humano': False
            }
        """
        
        # Buscar padrões no histórico
        similar_decisions = self._find_similar_decisions(context)
        
        if not similar_decisions:
            # Sem histórico: usar heurística default
            return {'escolhida': options[0], 'confianca': 0.5, 'escalada_para_humano': True}
        
        # Calcular confiança por opção
        confidence_scores = {}
        for option in options:
            success_rate = self._calculate_success_rate(option, similar_decisions)
            confidence_scores[option] = success_rate
        
        # Escolher melhor
        best_option = max(confidence_scores, key=confidence_scores.get)
        best_confidence = confidence_scores[best_option]
        
        # Decidir se escalona para humano
        escalada = best_confidence < confidence_threshold
        
        decision = {
            'escolhida': best_option,
            'confianca': best_confidence,
            'reasoning': f"{best_option} funcionou em {best_confidence:.1%} dos casos similares",
            'escalada_para_humano': escalada,
            'all_options': confidence_scores
        }
        
        self.decision_history.append(decision)
        return decision
    
    def _find_similar_decisions(self, context):
        """Buscar decisões similares no histórico"""
        # Similaridade por embedding ou hash
        similar = []
        for past_decision in self.decision_history:
            similarity = self._calculate_similarity(context, past_decision)
            if similarity > 0.7:  # 70% similar é suficiente
                similar.append(past_decision)
        return similar
    
    def _calculate_success_rate(self, option, similar_decisions):
        """Calcular taxa de sucesso para opção"""
        successes = sum(1 for d in similar_decisions if d.get('escolhida') == option and d.get('resultado') == 'sucesso')
        total = len([d for d in similar_decisions if d.get('escolhida') == option])
        return successes / total if total > 0 else 0.5
```

### Continuous Learning Daemon (v6.0)

```python
# File: maestro/continuous_learning.py
from apscheduler.schedulers.background import BackgroundScheduler

class ContinuousLearning:
    """Aprendizado contínuo executado todo dia (v6.0)"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        """Iniciar scheduler de aprendizado"""
        
        # Todos os dias às 2 AM
        self.scheduler.add_job(
            self.analyze_and_improve,
            'cron',
            hour=2, minute=0,
            id='daily_learning_loop'
        )
        self.scheduler.start()
    
    def analyze_and_improve(self):
        """Analisar últimas execuções e melhorar prompts"""
        
        print("🧠 Iniciando análise de aprendizado...")
        
        # 1. Pegar últimas 100 execuções
        last_projects = Project.find().order_by('-completed_at').limit(100)
        
        # 2. Agrupar por fase e calcular success rate
        for phase_num in range(1, 8):
            phases = [p for p in last_projects if p.phase_number == phase_num]
            
            success_count = sum(1 for p in phases if p.status == 'completed')
            success_rate = success_count / len(phases) if phases else 0
            
            print(f"   Phase {phase_num}: {success_rate:.1%} sucesso")
            
            # 3. Se success_rate < 85%, gerar novo prompt
            if success_rate < 0.85:
                print(f"      → Regenerando prompt para phase {phase_num}...")
                
                # Usar aprendizado anterior
                optimizer = PromptOptimizer()
                new_prompt = optimizer.generate_improved_prompt(
                    phase_num, 
                    last_projects
                )
                
                # Salvar nova versão
                PromptVersion.create(
                    phase_number=phase_num,
                    version=self._get_next_version(phase_num),
                    prompt_text=new_prompt,
                    reason='Auto-improved based on past performance'
                )
        
        print("✅ Análise de aprendizado completa")
```

---

## 🎯 TIMELINE DETALHADO v4.0-v6.0

```
SEMANA 1-2: v4.0 SPRINT 1 - REST API Foundation
├─ Implement REST endpoints (6h)
├─ Setup FastAPI + Uvicorn (4h)
├─ Database schema design (8h)
├─ Initial Postgres migration (4h)
├─ Tests (4h)
└─ Subtotal: 26h

SEMANA 3-4: v4.0 SPRINT 2 - Async Processing
├─ Redis setup + configuration (4h)
├─ Celery workers implementation (10h)
├─ Task queue structure (6h)
├─ Worker monitoring (Flower) (4h)
├─ Error handling + retries (6h)
└─ Subtotal: 30h

SEMANA 5-6: v4.0 SPRINT 3 - Scaling & Optimization
├─ Docker + docker-compose (8h)
├─ Load balancer (nginx) setup (6h)
├─ Horizontal scaling config (8h)
├─ Performance testing (6h)
├─ Monitoring + alerting setup (6h)
└─ Subtotal: 34h

SEMANA 6: v4.0 RELEASE
├─ Full end-to-end testing (10h)
├─ Documentation (6h)
├─ v4.0 AVALIACAO-CRITICA (2h)
└─ Subtotal: 18h

v4.0 TOTAL: 108h / Target: 150h (28% buffer para bugs/refinement)

───────────────────────────────────────────────────────

SEMANA 7-8: v5.0 SPRINT 1 - Learning Infrastructure
├─ Prompt versioning system (8h)
├─ A/B testing framework (12h)
├─ Statistical analysis (t-test, etc) (6h)
├─ Initial experiments (8h)
└─ Subtotal: 34h

SEMANA 9-10: v5.0 SPRINT 2 - Domain Adaptation
├─ Domain classifier (8h)
├─ Domain-specific prompt templates (12h)
├─ Auto-selection logic (8h)
├─ Testing por domain (8h)
└─ Subtotal: 36h

SEMANA 11-12: v5.0 SPRINT 3 - Adversarial Testing
├─ Adversarial test suite (12h)
├─ Edge case generator (8h)
├─ Stress testing (8h)
├─ Continuous integration (6h)
└─ Subtotal: 34h

SEMANA 12: v5.0 RELEASE
├─ Performance benchmarks (8h)
├─ Optimization passes (6h)
├─ v5.0 AVALIACAO-CRITICA (2h)
└─ Subtotal: 16h

v5.0 TOTAL: 120h / Target: 140h (14% buffer)

───────────────────────────────────────────────────────

SEMANA 13: v6.0 SPRINT 1 - Autonomous Decisions
├─ Decision engine implementation (12h)
├─ Pattern recognition (8h)
├─ Confidence scoring (8h)
├─ Tests (6h)
└─ Subtotal: 34h

SEMANA 14: v6.0 MAESTRO FINAL
├─ Continuous learning daemon (8h)
├─ Full system resilience (8h)
├─ End-to-end tests (4h)
├─ v6.0 AVALIACAO-CRITICA (2h)
├─ MANIFESTO-MAESTRO.md (2h)
└─ Subtotal: 24h

v6.0 TOTAL: 58h / Target: 50h

───────────────────────────────────────────────────────

TOTAL: 286h (vs planned 340h) → 8% BUFFER REMAINING
```

---

## 📊 SUCCESS METRICS v4.0-v6.0

| Métrica | v4.0 Goal | v5.0 Goal | v6.0 Goal |
|---------|-----------|-----------|-----------|
| **Score** | 85/100 | 95/100 | 100/100 |
| **Latência P99** | 500ms | 300ms | 200ms |
| **Throughput** | 200 proj/h | 400 proj/h | 600+ proj/h |
| **Success Rate** | 95% | 98% | 99%+ |
| **API Uptime** | 99.5% | 99.9% | 99.95% |
| **Test Coverage** | 75% | 85% | 95%+ |
| **Autonomous Decisions** | N/A | 30% | 80%+ |
| **Self-Correction Rate** | 50% | 70% | 90%+ |

---

## 🔄 QUALITY GATES v4.0-v6.0

### v4.0 Gates (SC1-SC5)
- SC1: API endpoints retornam 200 OK
- SC2: Async processing não bloqueia
- SC3: Database persiste corretamente
- SC4: Load balancer distribui workload
- SC5: Redis cache melhora performance 2x

### v5.0 Gates (LL1-LL5)
- LL1: Prompt versioning funciona
- LL2: A/B testing é statistically sound
- LL3: Learning loop melhora score
- LL4: Domain adaptation aumenta score por domain
- LL5: Adversarial tests detectam bugs

### v6.0 Gates (MA1-MA5)
- MA1: Autonomous decisions tomadas corretamente
- MA2: Continuous learning melhora sistema
- MA3: Creative problem solving funciona
- MA4: Full resilience (nenhuma falha fatal)
- MA5: Transparency (usuário sempre informado)

---

## 💡 KEY DECISIONS

✅ **Tech Stack:**
- FastAPI (async, fast, well-documented)
- PostgreSQL (ACID, scalable, reliable)
- Redis (caching, task queue, pub/sub)
- Celery (async tasks, distributed workers)
- Docker (containerization, deployment)

✅ **Architecture:**
- Microservices-ready (API decoupled from workers)
- Stateless API (scales horizontally)
- Message broker pattern (decouples phases)
- Database-backed state (not in-memory)

✅ **Monitoring:**
- Prometheus metrics (system health)
- Grafana dashboards (visualization)
- Flower (Celery monitoring)
- Structured logging (ELK stack ready)

---

## 📝 ARQUIVOS A CRIAR

```
v4.0/
├── api/
│   ├── main.py (FastAPI app)
│   ├── routes.py (endpoints)
│   ├── models.py (Pydantic schemas)
│   └── middleware.py (logging, error handling)
├── workers/
│   ├── celery_app.py
│   ├── tasks.py (async tasks)
│   └── config.py
├── db/
│   ├── models.py (SQLAlchemy)
│   ├── migrations/ (Alembic)
│   └── session.py
├── docker-compose.yml
├── nginx.conf
├── tests/
│   ├── test_api.py
│   ├── test_workers.py
│   └── test_db.py
└── requirements.txt

v5.0/
├── learning/
│   ├── prompt_optimizer.py
│   ├── domain_adapter.py
│   ├── adversarial_tester.py
│   └── a_b_test_framework.py
└── tests/
    ├── test_learning_loop.py
    └── test_domain_adaptation.py

v6.0/
├── maestro/
│   ├── decision_engine.py
│   ├── continuous_learning.py
│   ├── autonomous_agent.py
│   └── resilience_manager.py
└── tests/
    ├── test_autonomous_decisions.py
    └── test_resilience.py
```

---

**Status:** ✅ PLANEJAMENTO COMPLETO  
**Timeline:** 14 semanas  
**Investment:** $51.5k + 340h  
**Próximo:** Começar v4.0 Sprint 1

🚀 **PRONTO PARA IMPLEMENTAR?** 

Comando: `/implementacao v4.0`
