import json

from app.llm.client import LLMMessage


TASK_ASSISTANT_SYSTEM_PROMPT = """你是 AI 每日任务清单助手。
你只基于用户已经提供的任务、日期、可用时间、任务状态和反馈做整理建议。
不要凭空编造正式任务；如果提出新任务，只能作为 suggestion 返回。
所有输出必须是 JSON 对象，不要输出 Markdown、解释性前后缀或代码块。"""


def build_task_optimize_messages(payload: dict) -> list[LLMMessage]:
    user_prompt = {
        "instruction": "请优化用户输入的单个学习任务表达，使它更具体、可执行、可反馈。只返回建议，不要保存或覆盖原任务。",
        "required_json_shape": {
            "suggested_title": "优化后的任务标题",
            "suggested_description": "具体执行说明",
            "suggested_subject": "学科或主题",
            "suggested_estimated_minutes": 90,
            "suggested_priority": "medium",
            "reason": "为什么这样优化",
            "warnings": ["可选风险提示"],
        },
        "rules": [
            "不要替用户改变学习目标，只优化表达和执行粒度。",
            "如果原始任务过宽泛，说明如何收敛为当天可执行动作。",
            "estimated_minutes 必须是合理正整数。",
            "priority 只能是 low、medium、high、urgent。",
        ],
        "input": payload,
    }
    return [
        LLMMessage(role="system", content=TASK_ASSISTANT_SYSTEM_PROMPT),
        LLMMessage(role="user", content=json.dumps(user_prompt, ensure_ascii=False, default=str)),
    ]


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
        "instruction": "请对用户任务给出整理建议，包括分类、优先级、耗时估算和需要拆分的任务。",
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
            "task_id 必须来自输入任务。",
            "suggestion_type 只能是 estimate_time、split、adjust_priority、summarize。",
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


def build_calendar_supplement_messages(payload: dict) -> list[LLMMessage]:
    user_prompt = {
        "instruction": "请根据用户历史任务、当天已有任务、可用时间和反馈，提出少量当天补充任务建议。不要直接创建正式任务。",
        "required_json_shape": {
            "suggestions": [
                {
                    "title": "补充任务标题",
                    "description": "任务说明",
                    "category": "学习",
                    "subject": "数学",
                    "priority": "medium",
                    "estimated_minutes": 60,
                    "reason": "为什么适合补充到这一天",
                    "confidence": 0.75,
                    "risk_level": "low",
                }
            ]
        },
        "rules": [
            "只能基于输入中的用户任务和反馈，不要调用或引用院校知识库 RAG。",
            "不要编造用户没有提到的长期目标。",
            "默认建议 1 到 3 个任务。",
            "补充后总预计时间不能明显超过 available_minutes。",
            "如果当天已有任务已经接近可用时间，返回空 suggestions 并说明原因。",
            "priority 只能是 low、medium、high、urgent。",
            "risk_level 只能是 low、medium、high。",
        ],
        "input": payload,
    }
    return [
        LLMMessage(role="system", content=TASK_ASSISTANT_SYSTEM_PROMPT),
        LLMMessage(role="user", content=json.dumps(user_prompt, ensure_ascii=False, default=str)),
    ]
