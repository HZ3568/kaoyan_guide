from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.planner.ai_task_assistant import AiTaskAssistant
from app.planner.task_models import TaskAiSuggestion, TaskItem
from app.planner.task_schemas import (
    RagTaskRecommendationRequest,
    RagTaskRecommendationResponse,
    TaskAiSuggestionRead,
    TaskItemBulkCreateRequest,
    TaskItemBulkCreateResponse,
    TaskItemCreate,
    TaskItemRead,
    TaskItemUpdate,
    TaskOrganizeRequest,
    TaskOrganizeResponse,
    TaskSplitResponse,
)
from app.services.vector_index_service import VectorIndexService, VectorSearchResult


class TaskService:
    def __init__(
        self,
        db: Session,
        *,
        ai_assistant: AiTaskAssistant | None = None,
        vector_service: VectorIndexService | None = None,
    ) -> None:
        self.db = db
        self.ai_assistant = ai_assistant or AiTaskAssistant()
        self._vector_service = vector_service

    def create_task(self, user_id: int, payload: TaskItemCreate) -> TaskItemRead:
        task = TaskItem(user_id=user_id, **payload.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return TaskItemRead.model_validate(task)

    def bulk_create(self, user_id: int, payload: TaskItemBulkCreateRequest) -> TaskItemBulkCreateResponse:
        tasks = [TaskItem(user_id=user_id, **item.model_dump()) for item in payload.tasks]
        self.db.add_all(tasks)
        self.db.commit()
        for task in tasks:
            self.db.refresh(task)
        return TaskItemBulkCreateResponse(tasks=[TaskItemRead.model_validate(task) for task in tasks])

    def list_tasks(
        self,
        user_id: int,
        *,
        status_filter: str | None = None,
        category: str | None = None,
        subject: str | None = None,
        priority: str | None = None,
        deadline_before: date | None = None,
    ) -> list[TaskItemRead]:
        query = self.db.query(TaskItem).filter(TaskItem.user_id == user_id)
        if status_filter:
            query = query.filter(TaskItem.status == status_filter)
        if category:
            query = query.filter(TaskItem.category == category)
        if subject:
            query = query.filter(TaskItem.subject == subject)
        if priority:
            query = query.filter(TaskItem.priority == priority)
        if deadline_before:
            query = query.filter(TaskItem.deadline <= deadline_before)
        tasks = query.order_by(TaskItem.status.asc(), TaskItem.deadline.asc(), TaskItem.id.desc()).all()
        return [TaskItemRead.model_validate(task) for task in tasks]

    def update_task(self, user_id: int, task_id: int, payload: TaskItemUpdate) -> TaskItemRead:
        task = self._get_task(user_id, task_id)
        data = payload.model_dump(exclude_unset=True)
        if "parent_task_id" in data and data["parent_task_id"] == task.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task cannot be its own parent")
        for key, value in data.items():
            setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return TaskItemRead.model_validate(task)

    def archive_task(self, user_id: int, task_id: int) -> TaskItemRead:
        task = self._get_task(user_id, task_id)
        task.status = "archived"
        self.db.commit()
        self.db.refresh(task)
        return TaskItemRead.model_validate(task)

    def split_task(self, user_id: int, task_id: int) -> TaskSplitResponse:
        task = self._get_task(user_id, task_id)
        payload = self._task_payload(task)
        split_result = self.ai_assistant.split_task(payload)
        suggestion = TaskAiSuggestion(
            user_id=user_id,
            task_id=task.id,
            suggestion_type="split_task",
            suggestion_content=split_result,
            accepted=False,
        )
        self.db.add(suggestion)
        self.db.commit()
        self.db.refresh(task)
        self.db.refresh(suggestion)
        return TaskSplitResponse(
            task=TaskItemRead.model_validate(task),
            suggestions=[TaskAiSuggestionRead.model_validate(suggestion)],
            message="已生成拆分建议，原任务未被覆盖。",
        )

    def organize_tasks(self, user_id: int, payload: TaskOrganizeRequest) -> TaskOrganizeResponse:
        query = self.db.query(TaskItem).filter(TaskItem.user_id == user_id)
        if payload.status:
            query = query.filter(TaskItem.status.in_(payload.status))
        tasks = query.order_by(TaskItem.deadline.asc(), TaskItem.priority.desc(), TaskItem.id.asc()).limit(payload.limit).all()
        suggestions_payload = self.ai_assistant.organize_tasks(
            {"tasks": [self._task_payload(task) for task in tasks], "limit": payload.limit}
        )
        suggestions: list[TaskAiSuggestion] = []
        task_ids = {task.id for task in tasks}
        for item in suggestions_payload:
            task_id = item.get("task_id")
            if task_id not in task_ids:
                continue
            suggestion = TaskAiSuggestion(
                user_id=user_id,
                task_id=task_id,
                suggestion_type=item.get("suggestion_type") or "summarize",
                suggestion_content=item.get("content") or {},
                accepted=False,
            )
            self.db.add(suggestion)
            suggestions.append(suggestion)
        self.db.commit()
        for suggestion in suggestions:
            self.db.refresh(suggestion)
        return TaskOrganizeResponse(
            suggestions=[TaskAiSuggestionRead.model_validate(suggestion) for suggestion in suggestions],
            message="已生成任务池整理建议，未自动覆盖原任务。",
        )

    def recommend_from_rag(
        self,
        user_id: int,
        payload: RagTaskRecommendationRequest,
    ) -> RagTaskRecommendationResponse:
        rag_sources = self._retrieve_rag_sources(user_id=user_id, query=payload.query, top_k=payload.top_k)
        suggestion_payloads = self.ai_assistant.recommend_from_rag(
            {
                "query": payload.query,
                "max_tasks": payload.max_tasks,
                "rag_sources": rag_sources,
            }
        )
        suggestions: list[TaskAiSuggestion] = []
        for item in suggestion_payloads[: payload.max_tasks]:
            suggestion = TaskAiSuggestion(
                user_id=user_id,
                task_id=None,
                suggestion_type="today_plan",
                suggestion_content={
                    **item,
                    "source_type": "rag_recommendation",
                    "rag_sources": rag_sources,
                },
                accepted=False,
            )
            self.db.add(suggestion)
            suggestions.append(suggestion)
        self.db.commit()
        for suggestion in suggestions:
            self.db.refresh(suggestion)
        return RagTaskRecommendationResponse(
            suggestions=[TaskAiSuggestionRead.model_validate(suggestion) for suggestion in suggestions],
            message="已基于 RAG 资料生成候选任务建议，需要用户确认后再加入任务池。",
        )

    def _retrieve_rag_sources(self, *, user_id: int, query: str, top_k: int) -> list[dict]:
        try:
            vector_service = self._vector_service or VectorIndexService(self.db)
            results = vector_service.search(query=query, user_id=user_id, top_k=top_k)
        except Exception:
            return []
        return [self._rag_source_from_result(result) for result in results]

    @staticmethod
    def _rag_source_from_result(result: VectorSearchResult) -> dict:
        source = result.source or {}
        return {
            "chunk_id": result.chunk_id,
            "document_id": result.document_id,
            "score": result.score,
            "title": source.get("title"),
            "source": source.get("source"),
            "page_number": source.get("page_number") or result.page_number,
            "content_preview": result.content[:300],
            "metadata": result.metadata,
        }

    def _get_task(self, user_id: int, task_id: int) -> TaskItem:
        task = self.db.query(TaskItem).filter(TaskItem.id == task_id, TaskItem.user_id == user_id).first()
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    @staticmethod
    def _task_payload(task: TaskItem) -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "category": task.category,
            "subject": task.subject,
            "project": task.project,
            "priority": task.priority,
            "difficulty": task.difficulty,
            "estimated_minutes": task.estimated_minutes,
            "deadline": task.deadline,
            "status": task.status,
            "parent_task_id": task.parent_task_id,
            "is_splittable": task.is_splittable,
            "source_type": task.source_type,
            "source_ref": task.source_ref,
        }
