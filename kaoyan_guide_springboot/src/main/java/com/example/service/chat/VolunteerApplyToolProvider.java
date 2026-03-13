package com.example.service.chat;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class VolunteerApplyToolProvider implements ModuleToolProvider {
    /**
     * 声明当前工具配置归属“志愿填报”模块。
     */
    @Override
    public ModuleType moduleType() {
        return ModuleType.VOLUNTEER_APPLY;
    }

    /**
     * 返回志愿填报模块允许模型调用的工具函数名。
     */
    @Override
    public List<String> toolNames() {
        return List.of("addReservation", "queryReservationByPhone");
    }
}
