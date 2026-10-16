# -*- coding: utf-8 -*-
"""
Vertical Slice: Tasks Router
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from src.features.tasks.schemas import TaskCreate, TaskToggle, TaskOut
from src.features.tasks import service

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskOut], summary="Listar tarefas operacionais")
def get_tasks():
    return service.list_tasks()


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED, summary="Criar nova tarefa")
def create_task(data: TaskCreate):
    return service.create_task(data)


@router.patch("/{task_id}/toggle", response_model=TaskOut, summary="Alternar conclusão de tarefa")
def toggle_task(task_id: str, data: TaskToggle):
    task = service.toggle_task(task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return task
