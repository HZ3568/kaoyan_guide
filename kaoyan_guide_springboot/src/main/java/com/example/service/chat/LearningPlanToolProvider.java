package com.example.service.chat;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.List;

@Component
public class LearningPlanToolProvider implements ModuleToolProvider {
    /**
     * 声明当前工具配置归属“学习规划”模块。
     */
    @Override
    public ModuleType moduleType() {
        return ModuleType.LEARNING_PLAN;
    }

    /**
     * 学习规划模块当前不暴露工具调用能力，返回空列表。
     */
    @Override
    public List<String> toolNames() {
        return Collections.emptyList();
    }
}
