#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v4.0: DATABASE SESSION MANAGEMENT

Gerencia conexões, transactions, e operações CRUD
"""

import sys
from contextlib import contextmanager
from sqlalchemy.orm import Session
from datetime import datetime
from .models import (
    Project, ProjectPhase, PhaseLog, RetryHistory,
    PerformanceMetric, PromptExperiment,
    ProjectStatus, PhaseStatus, LogLevel, RetryStrategy,
    DatabaseSession
)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


class DatabaseManager:
    """Gerenciador de database com operações comuns"""

    def __init__(self, db_session: DatabaseSession):
        self.db = db_session

    # ========================================================================
    # PROJECT OPERATIONS
    # ========================================================================

    def create_project(self, ideia: str, opcoes: dict = None) -> Project:
        """Criar novo projeto"""
        session = self.db.get_session()
        try:
            project = Project(
                ideia=ideia,
                status=ProjectStatus.QUEUED,
                opcoes=opcoes or {}
            )
            session.add(project)
            session.commit()
            return project
        finally:
            session.close()

    def get_project(self, project_id: str) -> Project:
        """Obter projeto por ID"""
        session = self.db.get_session()
        try:
            return session.query(Project).filter(Project.id == project_id).first()
        finally:
            session.close()

    def update_project_status(self, project_id: str, status: ProjectStatus):
        """Atualizar status do projeto"""
        session = self.db.get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = status
                if status == ProjectStatus.PROCESSING:
                    project.started_at = datetime.utcnow()
                elif status in [ProjectStatus.COMPLETED, ProjectStatus.FAILED]:
                    project.completed_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()

    def get_projects_by_status(self, status: ProjectStatus) -> list:
        """Listar projetos por status"""
        session = self.db.get_session()
        try:
            return session.query(Project).filter(Project.status == status).all()
        finally:
            session.close()

    # ========================================================================
    # PHASE OPERATIONS
    # ========================================================================

    def create_phase(self, project_id: str, phase_num: int, phase_name: str) -> ProjectPhase:
        """Criar nova phase"""
        session = self.db.get_session()
        try:
            phase = ProjectPhase(
                project_id=project_id,
                phase_number=phase_num,
                phase_name=phase_name,
                status=PhaseStatus.PENDING
            )
            session.add(phase)
            session.commit()
            return phase
        finally:
            session.close()

    def update_phase_status(self, phase_id: str, status: PhaseStatus):
        """Atualizar status da phase"""
        session = self.db.get_session()
        try:
            phase = session.query(ProjectPhase).filter(ProjectPhase.id == phase_id).first()
            if phase:
                phase.status = status
                if status == PhaseStatus.PROCESSING:
                    phase.started_at = datetime.utcnow()
                elif status in [PhaseStatus.COMPLETED, PhaseStatus.FAILED]:
                    phase.completed_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()

    def get_project_phases(self, project_id: str) -> list:
        """Obter todas as phases de um projeto"""
        session = self.db.get_session()
        try:
            return session.query(ProjectPhase)\
                .filter(ProjectPhase.project_id == project_id)\
                .order_by(ProjectPhase.phase_number)\
                .all()
        finally:
            session.close()

    # ========================================================================
    # LOG OPERATIONS
    # ========================================================================

    def add_log(self, project_id: str, phase_id: str, level: LogLevel, message: str, stacktrace: str = None):
        """Adicionar log"""
        session = self.db.get_session()
        try:
            log = PhaseLog(
                project_id=project_id,
                phase_id=phase_id,
                level=level,
                message=message,
                stacktrace=stacktrace
            )
            session.add(log)
            session.commit()
        finally:
            session.close()

    def get_phase_logs(self, phase_id: str, level: LogLevel = None) -> list:
        """Obter logs de uma phase"""
        session = self.db.get_session()
        try:
            query = session.query(PhaseLog).filter(PhaseLog.phase_id == phase_id)
            if level:
                query = query.filter(PhaseLog.level == level)
            return query.order_by(PhaseLog.timestamp.desc()).all()
        finally:
            session.close()

    # ========================================================================
    # RETRY OPERATIONS
    # ========================================================================

    def add_retry(self, project_id: str, phase_id: str, attempt: int, strategy: RetryStrategy, status: str, error: str = None):
        """Registrar tentativa de retry"""
        session = self.db.get_session()
        try:
            retry = RetryHistory(
                project_id=project_id,
                phase_id=phase_id,
                attempt_number=attempt,
                strategy=strategy,
                status=status,
                error_message=error
            )
            session.add(retry)
            session.commit()
        finally:
            session.close()

    def get_retry_history(self, project_id: str) -> list:
        """Obter histórico de retries"""
        session = self.db.get_session()
        try:
            return session.query(RetryHistory)\
                .filter(RetryHistory.project_id == project_id)\
                .order_by(RetryHistory.created_at.desc())\
                .all()
        finally:
            session.close()

    # ========================================================================
    # METRICS OPERATIONS
    # ========================================================================

    def add_metric(self, project_id: str, metric_name: str, metric_value: float, tags: dict = None):
        """Adicionar métrica de performance"""
        session = self.db.get_session()
        try:
            metric = PerformanceMetric(
                project_id=project_id,
                metric_name=metric_name,
                metric_value=metric_value,
                tags=tags or {}
            )
            session.add(metric)
            session.commit()
        finally:
            session.close()

    def get_project_metrics(self, project_id: str) -> list:
        """Obter todas as métricas de um projeto"""
        session = self.db.get_session()
        try:
            return session.query(PerformanceMetric)\
                .filter(PerformanceMetric.project_id == project_id)\
                .order_by(PerformanceMetric.recorded_at.desc())\
                .all()
        finally:
            session.close()

    # ========================================================================
    # EXPERIMENT OPERATIONS (v5.0)
    # ========================================================================

    def create_experiment(self, project_id: str, phase_num: int, prompt_a: str, prompt_b: str) -> PromptExperiment:
        """Criar novo A/B experiment"""
        session = self.db.get_session()
        try:
            experiment = PromptExperiment(
                project_id=project_id,
                phase_number=phase_num,
                prompt_version_a=prompt_a,
                prompt_version_b=prompt_b
            )
            session.add(experiment)
            session.commit()
            return experiment
        finally:
            session.close()

    def update_experiment_results(self, experiment_id: str, score_a: float, score_b: float, winner: str, p_value: float):
        """Atualizar resultados do experiment"""
        session = self.db.get_session()
        try:
            exp = session.query(PromptExperiment).filter(PromptExperiment.id == experiment_id).first()
            if exp:
                exp.score_a = score_a
                exp.score_b = score_b
                exp.winner = winner
                exp.p_value = p_value
                exp.statistically_significant = p_value < 0.05
                exp.completed_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()

    # ========================================================================
    # ANALYTICS
    # ========================================================================

    def get_project_stats(self, project_id: str) -> dict:
        """Obter estatísticas de um projeto"""
        session = self.db.get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return {}

            phases = session.query(ProjectPhase).filter(ProjectPhase.project_id == project_id).all()
            retries = session.query(RetryHistory).filter(RetryHistory.project_id == project_id).all()
            logs = session.query(PhaseLog).filter(PhaseLog.project_id == project_id).all()

            return {
                'project_id': project_id,
                'status': project.status.value,
                'score': project.score_atual,
                'progress': project.progress,
                'phases': {
                    'total': len(phases),
                    'completed': sum(1 for p in phases if p.status == PhaseStatus.COMPLETED),
                    'failed': sum(1 for p in phases if p.status == PhaseStatus.FAILED)
                },
                'retries': {
                    'total': len(retries),
                    'successful': sum(1 for r in retries if r.status == 'success'),
                    'failed': sum(1 for r in retries if r.status == 'failed')
                },
                'logs': {
                    'total': len(logs),
                    'info': sum(1 for l in logs if l.level == LogLevel.INFO),
                    'warnings': sum(1 for l in logs if l.level == LogLevel.WARNING),
                    'errors': sum(1 for l in logs if l.level == LogLevel.ERROR)
                }
            }
        finally:
            session.close()

    def get_system_stats(self) -> dict:
        """Obter estatísticas do sistema inteiro"""
        session = self.db.get_session()
        try:
            projects = session.query(Project).all()

            return {
                'total_projects': len(projects),
                'by_status': {
                    'queued': sum(1 for p in projects if p.status == ProjectStatus.QUEUED),
                    'processing': sum(1 for p in projects if p.status == ProjectStatus.PROCESSING),
                    'completed': sum(1 for p in projects if p.status == ProjectStatus.COMPLETED),
                    'failed': sum(1 for p in projects if p.status == ProjectStatus.FAILED),
                    'cancelled': sum(1 for p in projects if p.status == ProjectStatus.CANCELLED)
                },
                'average_score': sum(p.score_atual for p in projects if p.score_atual) / len([p for p in projects if p.score_atual]) if any(p.score_atual for p in projects) else None
            }
        finally:
            session.close()
