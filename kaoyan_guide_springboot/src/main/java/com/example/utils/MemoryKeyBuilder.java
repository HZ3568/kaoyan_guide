package com.example.utils;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

@Component
public class MemoryKeyBuilder {
    private static final String PREFIX = "chat";
    private static final String DEFAULT_SESSION_ID = "default";
    private static final String REDIS_PREFIX = "chat:memory:";

    public String build(Integer userId, ModuleType moduleType, String sessionId) {
        if (userId == null) {
            throw new IllegalArgumentException("userId不能为空");
        }
        if (moduleType == null) {
            throw new IllegalArgumentException("moduleType不能为空");
        }
        String normalizedSessionId = normalizeSessionId(sessionId);
        return PREFIX + ":" + userId + ":" + moduleType.getCode() + ":" + normalizedSessionId;
    }

    public String toRedisKey(Object memoryId) {
        return REDIS_PREFIX + memoryId;
    }

    public String normalizeSessionId(String sessionId) {
        if (!StringUtils.hasText(sessionId)) {
            return DEFAULT_SESSION_ID;
        }
        String normalized = sessionId.trim().replace(":", "_");
        if (!StringUtils.hasText(normalized)) {
            return DEFAULT_SESSION_ID;
        }
        return normalized;
    }

    public String extractModuleType(String memoryKey) {
        String[] parts = split(memoryKey);
        return parts == null ? "" : parts[2];
    }

    public String extractSessionId(String memoryKey) {
        String[] parts = split(memoryKey);
        return parts == null ? "" : parts[3];
    }

    private String[] split(String memoryKey) {
        if (!StringUtils.hasText(memoryKey)) {
            return null;
        }
        String[] parts = memoryKey.split(":", 4);
        if (parts.length < 4) {
            return null;
        }
        if (!PREFIX.equals(parts[0])) {
            return null;
        }
        return parts;
    }
}
