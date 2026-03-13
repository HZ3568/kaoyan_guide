package com.example.service.chat;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Service;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;

@Service
public class ConversationContextService {
    private final Map<ModuleType, ModuleToolProvider> toolProviders = new EnumMap<>(ModuleType.class);
    private final Map<ModuleType, ModulePromptProvider> promptProviders = new EnumMap<>(ModuleType.class);

    /**
     * 收集各模块的工具提供器与提示词提供器，建立模块到配置的映射表。
     */
    public ConversationContextService(List<ModuleToolProvider> toolProviderList,
            List<ModulePromptProvider> promptProviderList) {
        for (ModuleToolProvider provider : toolProviderList) {
            toolProviders.put(provider.moduleType(), provider);
        }
        for (ModulePromptProvider provider : promptProviderList) {
            promptProviders.put(provider.moduleType(), provider);
        }
    }

    /**
     * 获取模块可用工具名列表。
     * 学习规划模块强制返回空列表，确保不会挂载外部工具。
     */
    public List<String> getTools(ModuleType moduleType) {
        ModuleToolProvider provider = toolProviders.get(moduleType);
        if (provider == null) {
            return List.of();
        }
        if (moduleType == ModuleType.LEARNING_PLAN) {
            return List.of();
        }
        return List.copyOf(provider.toolNames());
    }

    /**
     * 获取模块系统提示词资源路径。
     * 若模块未注册提示词，直接抛错，避免静默使用错误配置。
     */
    public String getPromptResource(ModuleType moduleType) {
        ModulePromptProvider provider = promptProviders.get(moduleType);
        if (provider == null) {
            throw new IllegalArgumentException("未配置模块提示词: " + moduleType.getCode());
        }
        return provider.promptResource();
    }

    /**
     * 判断是否启用 RAG 检索增强。
     * 当前仅志愿填报模块启用检索。
     */
    public boolean isRagEnabled(ModuleType moduleType) {
        return moduleType == ModuleType.VOLUNTEER_APPLY;
    }
}
