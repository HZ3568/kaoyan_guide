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

    public ConversationContextService(List<ModuleToolProvider> toolProviderList, List<ModulePromptProvider> promptProviderList) {
        for (ModuleToolProvider provider : toolProviderList) {
            toolProviders.put(provider.moduleType(), provider);
        }
        for (ModulePromptProvider provider : promptProviderList) {
            promptProviders.put(provider.moduleType(), provider);
        }
    }

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

    public String getPromptResource(ModuleType moduleType) {
        ModulePromptProvider provider = promptProviders.get(moduleType);
        if (provider == null) {
            throw new IllegalArgumentException("未配置模块提示词: " + moduleType.getCode());
        }
        return provider.promptResource();
    }

    public boolean isRagEnabled(ModuleType moduleType) {
        return moduleType == ModuleType.VOLUNTEER_APPLY;
    }
}
