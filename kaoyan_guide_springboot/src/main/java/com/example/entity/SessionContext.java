package com.example.entity;

import com.example.common.enums.ModuleType;

public class SessionContext {
    private final Integer userId;
    private final ModuleType moduleType;
    private final String sessionId;
    private final String memoryKey;

    public SessionContext(Integer userId, ModuleType moduleType, String sessionId, String memoryKey) {
        this.userId = userId;
        this.moduleType = moduleType;
        this.sessionId = sessionId;
        this.memoryKey = memoryKey;
    }

    public Integer getUserId() {
        return userId;
    }

    public ModuleType getModuleType() {
        return moduleType;
    }

    public String getSessionId() {
        return sessionId;
    }

    public String getMemoryKey() {
        return memoryKey;
    }
}
