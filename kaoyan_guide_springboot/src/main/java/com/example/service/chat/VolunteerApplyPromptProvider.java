package com.example.service.chat;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Component;

@Component
public class VolunteerApplyPromptProvider implements ModulePromptProvider {
    @Override
    public ModuleType moduleType() {
        return ModuleType.VOLUNTEER_APPLY;
    }

    @Override
    public String promptResource() {
        return "prompts/volunteer_apply_system_prompt.txt";
    }
}
