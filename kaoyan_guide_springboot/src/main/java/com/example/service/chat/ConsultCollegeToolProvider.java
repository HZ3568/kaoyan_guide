package com.example.service.chat;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class ConsultCollegeToolProvider implements ModuleToolProvider {
    /**
     * 声明当前工具配置归属“考研院校咨询”模块。
     */
    @Override
    public ModuleType moduleType() {
        return ModuleType.CONSULT_COLLEGE;
    }

    /**
     * 返回考研院校咨询模块允许模型调用的工具函数名。
     */
    @Override
    public List<String> toolNames() {
        return List.of("compareSchools");
    }
}
