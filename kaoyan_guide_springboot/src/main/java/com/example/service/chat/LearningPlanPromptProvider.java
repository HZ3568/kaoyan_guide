package com.example.service.chat;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Component;

@Component
public class LearningPlanPromptProvider implements ModulePromptProvider {
    @Override
    public ModuleType moduleType() {
        return ModuleType.LEARNING_PLAN;
    }

    @Override
    public String promptResource() {
        return "prompts/learning_plan_system_prompt.txt";
    }
}
