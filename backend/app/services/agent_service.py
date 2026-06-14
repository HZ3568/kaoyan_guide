class AgentService:
    """Agent 服务占位。

    后续可以引入 LangGraph，将学习规划拆成：画像读取、资料检索、计划生成、规则校验、任务保存、反馈调整。
    """

    def run(self, user_input: str) -> dict:
        return {"message": "Agent workflow placeholder", "input": user_input}
