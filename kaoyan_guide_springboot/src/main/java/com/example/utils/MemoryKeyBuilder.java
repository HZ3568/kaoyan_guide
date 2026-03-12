package com.example.utils;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.util.regex.Pattern;

@Component
public class MemoryKeyBuilder {
    private static final String REDIS_PREFIX = "chat:memory:";
    private static final Pattern SESSION_ID_PATTERN = Pattern.compile("^[A-Za-z0-9_-]{1,128}$");

    public String build(Integer userId, ModuleType moduleType, String sessionId) {
        if (userId == null) {
            throw new IllegalArgumentException("userId不能为空");
        }
        if (moduleType == null) {
            throw new IllegalArgumentException("moduleType不能为空");
        }
        if (!StringUtils.hasText(sessionId)) {
            throw new IllegalArgumentException("sessionId不能为空");
        }
        String normalizedSessionId = sessionId.trim();
        if (!isValidSessionId(normalizedSessionId)) {
            throw new IllegalArgumentException("sessionId格式非法");
        }
        return userId + ":" + moduleType.getCode() + ":" + normalizedSessionId;
    }

    public String toRedisKey(String memoryId) {
        return REDIS_PREFIX + memoryId;
    }

    public MemoryIdentity parseMemoryId(String memoryId) {
        if (!StringUtils.hasText(memoryId)) {
            return null;
        }
        String[] parts = memoryId.trim().split(":");
        if (parts.length != 3) {
            return null;
        }
        Integer userId;
        try {
            userId = Integer.valueOf(parts[0]);
        } catch (NumberFormatException e) {
            return null;
        }
        ModuleType moduleType;
        try {
            moduleType = ModuleType.fromCode(parts[1]);
        } catch (Exception e) {
            return null;
        }
        String sessionId = parts[2].trim();
        if (!isValidSessionId(sessionId)) {
            return null;
        }
        return new MemoryIdentity(userId, moduleType.getCode(), sessionId);
    }

    private boolean isValidSessionId(String sessionId) {
        return SESSION_ID_PATTERN.matcher(sessionId).matches();
    }

    public static class MemoryIdentity {
        private final Integer userId;
        private final String moduleType;
        private final String sessionId;

        public MemoryIdentity(Integer userId, String moduleType, String sessionId) {
            this.userId = userId;
            this.moduleType = moduleType;
            this.sessionId = sessionId;
        }

        public Integer getUserId() {
            return userId;
        }

        public String getModuleType() {
            return moduleType;
        }

        public String getSessionId() {
            return sessionId;
        }
    }
}
