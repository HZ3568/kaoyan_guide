package com.example.service.chat;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.List;

@Component
public class LearningPlanToolProvider implements ModuleToolProvider {
    @Override
    public ModuleType moduleType() {
        return ModuleType.LEARNING_PLAN;
    }

    @Override
    public List<String> toolNames() {
        return Collections.emptyList();
    }
}
