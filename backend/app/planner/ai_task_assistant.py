import json
import re
from typing import Any

from app.llm.client import LLMClient, LLMError, get_llm_client
from app.planner.prompt_templates import (
    build_calendar_supplement_messages,
    build_task_optimize_messages,
    build_task_organize_messages,
    build_task_split_messages,
    build_today_plan_messages,
)


class AiTaskAssistant:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or get_llm_client()

    def optimize_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        fallback = self._fallback_optimize(payload)
        try:
            response = self.llm_client.generate(build_task_optimize_messages(payload))
            data = self._parse_json_response(response.content)
        except (LLMError, ValueError, json.JSONDecodeError, TypeError):
            return fallback
        if not isinstance(data, dict):
            return fallback
        title = str(data.get("suggested_title") or "").strip()
        if not title:
            return fallback
        warnings = data.get("warnings")
        return {
            "suggested_title": title[:255],
            "suggested_description": str(data.get("suggested_description") or fallback["suggested_description"])[:1000],
            "suggested_subject": str(data.get("suggested_subject") or payload.get("subject") or "")[:64] or None,
            "suggested_estimated_minutes": self._safe_minutes(
                data.get("suggested_estimated_minutes"),
                default=fallback["suggested_estimated_minutes"],
            ),
            "suggested_priority": self._safe_priority(data.get("suggested_priority")),
            "reason": str(data.get("reason") or fallback["reason"])[:1000],
            "warnings": [str(item)[:300] for item in warnings[:5]] if isinstance(warnings, list) else [],
        }

    def split_task(self, task_payload: dict[str, Any]) -> dict[str, Any]:
        fallback = self._fallback_split(task_payload)
        try:
            response = self.llm_client.generate(build_task_split_messages(task_payload))
            data = self._parse_json_response(response.content)
        except (LLMError, ValueError, json.JSONDecodeError, TypeError):
            return fallback
        subtasks = data.get("subtasks") if isinstance(data, dict) else None
        if not isinstance(subtasks, list) or not subtasks:
            return fallback
        return {
            "summary": str(data.get("summary") or "已根据任务信息给出拆分建议。")[:500],
            "subtasks": [self._normalize_subtask(item) for item in subtasks if isinstance(item, dict)][:8],
        }

    def organize_tasks(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        fallback = self._fallback_organize(payload)
        try:
            response = self.llm_client.generate(build_task_organize_messages(payload))
            data = self._parse_json_response(response.content)
        except (LLMError, ValueError, json.JSONDecodeError, TypeError):
            return fallback
        suggestions = data.get("suggestions") if isinstance(data, dict) else None
        if not isinstance(suggestions, list):
            return fallback
        normalized = [self._normalize_organize_suggestion(item) for item in suggestions if isinstance(item, dict)]
        return [item for item in normalized if item][:100] or fallback

    def explain_today_plan(self, payload: dict[str, Any]) -> dict[str, Any]:
        fallback = self._fallback_today_plan(payload)
        try:
            response = self.llm_client.generate(build_today_plan_messages(payload))
            data = self._parse_json_response(response.content)
        except (LLMError, ValueError, json.JSONDecodeError, TypeError):
            return fallback
        if not isinstance(data, dict):
            return fallback
        task_ids = {task.get("id") for task in payload.get("selected_tasks", [])}
        reasons: dict[int, dict[str, str]] = {}
        for item in data.get("tasks") or []:
            if not isinstance(item, dict):
                continue
            task_id = item.get("task_id")
            if task_id not in task_ids:
                continue
            reason = str(item.get("reason") or "").strip()
            advice = str(item.get("execution_advice") or "").strip()
            reasons[int(task_id)] = {
                "reason": reason[:1000] if reason else fallback["task_reasons"].get(task_id, {}).get("reason", ""),
                "execution_advice": advice[:1000],
            }
        summary = str(data.get("summary") or fallback["summary"]).strip()[:1000]
        return {
            "summary": summary or fallback["summary"],
            "task_reasons": reasons or fallback["task_reasons"],
            "suggestions": data.get("suggestions") if isinstance(data.get("suggestions"), list) else [],
        }

    def supplement_calendar_tasks(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        fallback = self._fallback_supplement(payload)
        try:
            response = self.llm_client.generate(build_calendar_supplement_messages(payload))
            data = self._parse_json_response(response.content)
        except (LLMError, ValueError, json.JSONDecodeError, TypeError):
            return fallback
        suggestions = data.get("suggestions") if isinstance(data, dict) else None
        if not isinstance(suggestions, list):
            return fallback
        normalized: list[dict[str, Any]] = []
        for item in suggestions:
            if not isinstance(item, dict) or not item.get("title"):
                continue
            normalized.append(
                {
                    "title": str(item.get("title"))[:255],
                    "description": str(item.get("description") or "")[:1000],
                    "category": str(item.get("category") or "学习")[:64],
                    "subject": str(item.get("subject") or "")[:64] or None,
                    "priority": self._safe_priority(item.get("priority")),
                    "estimated_minutes": self._safe_minutes(item.get("estimated_minutes"), default=60),
                    "reason": str(item.get("reason") or "")[:1000],
                    "source_type": "ai_supplement",
                    "confidence": self._safe_float(item.get("confidence")),
                    "risk_level": item.get("risk_level") if item.get("risk_level") in {"low", "medium", "high"} else "medium",
                }
            )
        max_new_tasks = int(payload.get("max_new_tasks") or 3)
        return normalized[:max_new_tasks] or fallback

    @staticmethod
    def _parse_json_response(content: str) -> Any:
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text).strip()
            text = re.sub(r"```$", "", text).strip()
        if not text.startswith("{"):
            match = re.search(r"\{.*\}", text, flags=re.S)
            if not match:
                raise ValueError("LLM response does not contain a JSON object")
            text = match.group(0)
        return json.loads(text)

    @classmethod
    def _fallback_optimize(cls, payload: dict[str, Any]) -> dict[str, Any]:
        raw_title = str(payload.get("raw_title") or payload.get("title") or "学习任务").strip()
        subject = str(payload.get("subject") or "").strip() or None
        minutes = cls._safe_minutes(payload.get("estimated_minutes"), default=60)
        suggested_title = raw_title
        if not any(word in raw_title for word in ["完成", "整理", "复盘", "练习", "修改", "阅读"]):
            suggested_title = f"完成{subject or ''}{raw_title}".strip()
        description = str(payload.get("raw_description") or "").strip()
        if not description:
            description = "明确本次产出，执行后记录完成情况、实际用时和需要继续推进的问题。"
        return {
            "suggested_title": suggested_title[:255],
            "suggested_description": description[:1000],
            "suggested_subject": subject,
            "suggested_estimated_minutes": minutes,
            "suggested_priority": cls._safe_priority(payload.get("priority")),
            "reason": "LLM 不可用时按任务标题、学科、预计用时生成可执行表达建议。",
            "warnings": ["这是规则兜底建议，请在保存前人工确认。"],
        }

    @classmethod
    def _fallback_split(cls, task_payload: dict[str, Any]) -> dict[str, Any]:
        title = str(task_payload.get("title") or "任务")
        total_minutes = cls._safe_minutes(task_payload.get("estimated_minutes"), default=120)
        part_minutes = max(30, min(90, total_minutes // 3 or 45))
        return {
            "summary": "LLM 不可用时按准备、执行、复盘三个步骤给出拆分建议。",
            "subtasks": [
                {
                    "title": f"{title}：梳理目标和资料",
                    "description": "明确产出、收集资料并列出执行清单。",
                    "estimated_minutes": part_minutes,
                    "priority": cls._safe_priority(task_payload.get("priority")),
                    "difficulty": "normal",
                    "reason": "先降低任务不确定性，避免直接进入大任务。",
                },
                {
                    "title": f"{title}：完成核心推进",
                    "description": "集中处理最关键的部分，保留问题记录。",
                    "estimated_minutes": part_minutes,
                    "priority": cls._safe_priority(task_payload.get("priority")),
                    "difficulty": cls._safe_difficulty(task_payload.get("difficulty")),
                    "reason": "把大任务拆成可在单次学习时间内完成的核心块。",
                },
                {
                    "title": f"{title}：整理结果并复盘",
                    "description": "整理产出、记录阻塞点和下一步动作。",
                    "estimated_minutes": part_minutes,
                    "priority": "medium",
                    "difficulty": "easy",
                    "reason": "通过复盘把任务成果固化，便于后续继续推进。",
                },
            ],
        }

    @classmethod
    def _fallback_organize(cls, payload: dict[str, Any]) -> list[dict[str, Any]]:
        suggestions: list[dict[str, Any]] = []
        for task in payload.get("tasks", [])[:50]:
            if not isinstance(task, dict):
                continue
            task_id = task.get("id")
            if not task_id:
                continue
            if not task.get("category"):
                suggestions.append(
                    {
                        "task_id": task_id,
                        "suggestion_type": "summarize",
                        "content": {
                            "category": task.get("subject") or task.get("project") or "待分类",
                            "reason": "任务缺少分类，建议先补全分类便于日期任务统计和筛选。",
                        },
                    }
                )
            if cls._safe_minutes(task.get("estimated_minutes"), default=60) >= 180 and task.get("is_splittable", True):
                suggestions.append(
                    {
                        "task_id": task_id,
                        "suggestion_type": "split",
                        "content": {"reason": "预计耗时较长，建议拆成 30-90 分钟的子任务后再安排。"},
                    }
                )
        return suggestions[:100]

    @staticmethod
    def _fallback_today_plan(payload: dict[str, Any]) -> dict[str, Any]:
        selected = payload.get("selected_tasks", [])
        task_reasons = {
            task["id"]: {
                "reason": task.get("rule_reason") or "根据截止日期、优先级和可用时间由规则系统选入日期任务建议。",
                "execution_advice": "先明确本次最小产出，完成后记录实际耗时和阻塞点。",
            }
            for task in selected
            if isinstance(task, dict) and task.get("id")
        }
        return {
            "summary": "日期任务建议由规则系统按截止日期、优先级、估计耗时和任务状态生成。",
            "task_reasons": task_reasons,
            "suggestions": [],
        }

    @classmethod
    def _fallback_supplement(cls, payload: dict[str, Any]) -> list[dict[str, Any]]:
        available_minutes = cls._safe_minutes(payload.get("available_minutes"), default=120)
        existing_minutes = sum(
            cls._safe_minutes(task.get("estimated_minutes") or task.get("planned_minutes"), default=0)
            for task in payload.get("today_tasks", [])
            if isinstance(task, dict)
        )
        if existing_minutes >= int(available_minutes * 0.9):
            return []
        remaining = max(available_minutes - existing_minutes, 15)
        suggestions: list[dict[str, Any]] = []
        recent_tasks = [task for task in payload.get("recent_tasks", []) if isinstance(task, dict)]
        candidates = [
            task for task in recent_tasks
            if task.get("status") in {"delayed", "skipped", "overdue"}
        ] or [
            task for task in recent_tasks
            if task.get("status") in {"pending", "in_progress", "scheduled"}
        ]
        for task in candidates[: int(payload.get("max_new_tasks") or 3)]:
            if remaining < 15:
                break
            title = str(task.get("title") or "推进未完成任务")[:255]
            minutes = min(cls._safe_minutes(task.get("estimated_minutes"), default=45), remaining, 90)
            suggestions.append(
                {
                    "title": f"继续推进：{title}",
                    "description": str(task.get("description") or "补上近期未完成或需要继续推进的任务。")[:1000],
                    "category": task.get("category") or "学习",
                    "subject": task.get("subject"),
                    "priority": cls._safe_priority(task.get("priority")),
                    "estimated_minutes": minutes,
                    "reason": "根据近期延期、未完成或进行中任务给出补充建议，需用户确认后创建。",
                    "source_type": "ai_supplement",
                    "confidence": 0.6,
                    "risk_level": "medium" if task.get("status") in {"delayed", "skipped", "overdue"} else "low",
                }
            )
            remaining -= minutes
        if suggestions:
            return suggestions
        if remaining >= 30:
            return [
                {
                    "title": "整理今日学习复盘",
                    "description": "回顾当天已完成任务，记录实际用时、阻塞点和下一步最小动作。",
                    "category": "复盘",
                    "subject": None,
                    "priority": "medium",
                    "estimated_minutes": min(30, remaining),
                    "reason": "当天仍有可用时间且缺少可直接推进的历史任务，建议安排轻量复盘。",
                    "source_type": "ai_supplement",
                    "confidence": 0.5,
                    "risk_level": "low",
                }
            ]
        return []

    @classmethod
    def _normalize_subtask(cls, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "title": str(item.get("title") or "子任务")[:255],
            "description": str(item.get("description") or "")[:1000],
            "estimated_minutes": cls._safe_minutes(item.get("estimated_minutes"), default=45),
            "priority": cls._safe_priority(item.get("priority")),
            "difficulty": cls._safe_difficulty(item.get("difficulty")),
            "reason": str(item.get("reason") or "")[:1000],
        }

    @classmethod
    def _normalize_organize_suggestion(cls, item: dict[str, Any]) -> dict[str, Any] | None:
        task_id = item.get("task_id")
        if not isinstance(task_id, int):
            return None
        suggestion_type = item.get("suggestion_type")
        if suggestion_type == "split_task":
            suggestion_type = "split"
        if suggestion_type not in {"estimate_time", "split", "adjust_priority", "summarize"}:
            suggestion_type = "summarize"
        content = item.get("content")
        if not isinstance(content, dict):
            content = {"text": str(content or "")}
        if "priority" in content:
            content["priority"] = cls._safe_priority(content.get("priority"))
        if "estimated_minutes" in content:
            content["estimated_minutes"] = cls._safe_minutes(content.get("estimated_minutes"), default=60)
        return {
            "task_id": task_id,
            "suggestion_type": suggestion_type,
            "content": content,
        }

    @staticmethod
    def _safe_minutes(value: Any, *, default: int) -> int:
        try:
            minutes = int(value)
        except (TypeError, ValueError):
            return default
        return min(max(minutes, 0), 10000)

    @staticmethod
    def _safe_priority(value: Any) -> str:
        return value if value in {"low", "medium", "high", "urgent"} else "medium"

    @staticmethod
    def _safe_difficulty(value: Any) -> str:
        return value if value in {"easy", "normal", "hard", "very_hard"} else "normal"

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return min(max(number, 0.0), 1.0)
