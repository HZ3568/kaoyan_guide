package com.example.service.chat;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Component;

@Component
public class ConsultCollegePromptProvider implements ModulePromptProvider {
    /**
     * 声明当前提示词配置归属“考研院校咨询”模块。
     */
    @Override
    public ModuleType moduleType() {
        return ModuleType.CONSULT_COLLEGE;
    }

    /**
     * 返回考研院校咨询模块系统提示词路径。
     */
    @Override
    public String promptResource() {
        return "prompts/consult_college_system_prompt.txt";
    }
}
