import json

from app.llm.client import LLMMessage


TASK_ASSISTANT_SYSTEM_PROMPT = """你是 AI 每日任务清单助手。
你只基于用户已经提供的任务池、日期、可用时间、任务状态和反馈做整理建议。
不要凭空编造正式任务；如果提出新任务，只能作为 suggestion 返回。
所有输出必须是 JSON 对象，不要输出 Markdown、解释性前后缀或代码块。"""


def build_task_split_messages(task_payload: dict) -> list[LLMMessage]:
    user_prompt = {
        "instruction": "请把这个大任务拆成可执行子任务建议。不要修改原任务，不要直接创建正式任务。",
        "required_json_shape": {
            "summary": "一句话说明拆分思路",
            "subtasks": [
                {
                    "title": "子任务标题",
                    "description": "执行说明",
                    "estimated_minutes": 45,
                    "priority": "medium",
                    "difficulty": "normal",
                    "reason": "为什么这样拆",
                }
            ],
        },
        "rules": [
            "subtasks 数量建议 2 到 6 个。",
            "每个子任务必须来自原任务，不要引入无关事项。",
            "estimated_minutes 必须是合理正整数。",
            "priority 只能是 low、medium、high、urgent。",
        ],
        "task": task_payload,
    }
    return [
        LLMMessage(role="system", content=TASK_ASSISTANT_SYSTEM_PROMPT),
        LLMMessage(role="user", content=json.dumps(user_prompt, ensure_ascii=False, default=str)),
    ]


def build_task_organize_messages(payload: dict) -> list[LLMMessage]:
    user_prompt = {
        "instruction": "请对任务池给出整理建议，包括分类、优先级、耗时估算和需要拆分的任务。",
        "required_json_shape": {
            "suggestions": [
                {
                    "task_id": 1,
                    "suggestion_type": "estimate_time",
                    "content": {
                        "estimated_minutes": 90,
                        "priority": "high",
                        "category": "项目",
                        "reason": "建议原因",
                    },
                }
            ]
        },
        "rules": [
            "不要覆盖用户原始任务，只返回建议。",
            "task_id 必须来自输入任务池。",
            "suggestion_type 只能是 estimate_time、split_task、adjust_priority、summarize。",
            "无法判断时少给建议，不要编造。",
        ],
        "input": payload,
    }
    return [
        LLMMessage(role="system", content=TASK_ASSISTANT_SYSTEM_PROMPT),
        LLMMessage(role="user", content=json.dumps(user_prompt, ensure_ascii=False, default=str)),
    ]


def build_today_plan_messages(payload: dict) -> list[LLMMessage]:
    user_prompt = {
        "instruction": "请解释规则系统选出的今日任务，并给出执行建议。不要新增正式任务。",
        "required_json_shape": {
            "summary": "今天安排的总体原因",
            "tasks": [
                {
                    "task_id": 1,
                    "reason": "推荐这个任务的原因",
                    "execution_advice": "执行建议",
                }
            ],
            "suggestions": [
                {
                    "title": "可选建议任务",
                    "reason": "为什么建议，但不要加入正式计划",
                }
            ],
        },
        "rules": [
            "task_id 必须来自 selected_tasks。",
            "总预计时间不能明显超过 available_minutes。",
            "优先说明 deadline、priority、延期情况和长期任务推进原因。",
            "如果任务过大，只建议拆分，不要把拆分结果加入正式今日计划。",
        ],
        "input": payload,
    }
    return [
        LLMMessage(role="system", content=TASK_ASSISTANT_SYSTEM_PROMPT),
        LLMMessage(role="user", content=json.dumps(user_prompt, ensure_ascii=False, default=str)),
    ]


def build_rag_task_recommendation_messages(payload: dict) -> list[LLMMessage]:
    user_prompt = {
        "instruction": "请基于 RAG 检索资料提出候选学习任务建议，不能直接加入任务池。",
        "required_json_shape": {
            "suggestions": [
                {
                    "title": "候选任务标题",
                    "description": "任务说明",
                    "category": "考研复习",
                    "subject": "专业课",
                    "priority": "medium",
                    "estimated_minutes": 60,
                    "source_ref": {"chunk_id": 1, "document_id": 2},
                    "reason": "来源依据",
                }
            ]
        },
        "rules": [
            "每个建议必须能追溯到 rag_sources 中的 chunk_id 或 document_id。",
            "涉及院校、参考书、考试科目、分数线、招生人数时必须引用来源。",
            "不要输出正式任务状态，只输出建议。",
        ],
        "input": payload,
    }
    return [
        LLMMessage(role="system", content=TASK_ASSISTANT_SYSTEM_PROMPT),
        LLMMessage(role="user", content=json.dumps(user_prompt, ensure_ascii=False, default=str)),
    ]
