package com.example.service.chat;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Component;

@Component
public class LearningPlanPromptProvider implements ModulePromptProvider {
    /**
     * 声明当前提示词配置归属“学习规划”模块。
     */
    @Override
    public ModuleType moduleType() {
        return ModuleType.LEARNING_PLAN;
    }

    /**
     * 返回学习规划模块系统提示词路径。
     */
    @Override
    public String promptResource() {
        return "prompts/learning_plan_system_prompt.txt";
    }
}
