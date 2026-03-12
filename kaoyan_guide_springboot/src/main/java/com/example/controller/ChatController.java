package com.example.controller;

import com.example.common.enums.ModuleType;
import com.example.entity.Account;
import com.example.service.ChatGatewayService;
import com.example.utils.TokenUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

import jakarta.servlet.http.HttpServletResponse;

import java.util.UUID;

@RestController
public class ChatController {
    @Autowired
    private ChatGatewayService chatGatewayService;

    @RequestMapping(value = "/chat", produces = "text/event-stream;charset=UTF-8")
    public Flux<String> chat(@RequestParam("message") String message,
                             @RequestParam("moduleType") String moduleType,
                             @RequestParam(value = "sessionId", required = false) String sessionId,
                             @RequestParam(value = "memoryId", required = false) String legacyMemoryId,
                             HttpServletResponse response) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || currentUser.getId() == null) {
            throw new RuntimeException("未登录或登录已失效");
        }
        String effectiveSessionId = sessionId;
        if (!StringUtils.hasText(effectiveSessionId)) {
            effectiveSessionId = resolveLegacySessionId(legacyMemoryId);
        }
        if (!StringUtils.hasText(effectiveSessionId)) {
            effectiveSessionId = UUID.randomUUID().toString();
        }
        response.setHeader("X-Session-Id", effectiveSessionId);
        ModuleType targetModule = ModuleType.fromCode(moduleType);
        return chatGatewayService.chat(currentUser.getId(), targetModule, effectiveSessionId, message);
    }

    private String resolveLegacySessionId(String legacyMemoryId) {
        if (!StringUtils.hasText(legacyMemoryId)) {
            return null;
        }
        String normalized = legacyMemoryId.trim();
        int index = normalized.lastIndexOf(':');
        if (index < 0 || index == normalized.length() - 1) {
            return normalized;
        }
        return normalized.substring(index + 1).trim();
    }
}
