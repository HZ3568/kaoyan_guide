package com.example.service.chat;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Component;

@Component
public class VolunteerApplyPromptProvider implements ModulePromptProvider {
    /**
     * 声明当前提示词配置归属“志愿填报”模块。
     */
    @Override
    public ModuleType moduleType() {
        return ModuleType.VOLUNTEER_APPLY;
    }

    /**
     * 返回志愿填报模块系统提示词路径。
     */
    @Override
    public String promptResource() {
        return "prompts/volunteer_apply_system_prompt.txt";
    }
}
