package com.example.controller;

import com.example.common.enums.ModuleType;
import com.example.entity.Account;
import com.example.service.ChatGatewayService;
import com.example.utils.TokenUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.util.StringUtils;
import reactor.core.publisher.Flux;

@RestController
public class ChatController {
    @Autowired
    private ChatGatewayService chatGatewayService;

    @RequestMapping(value = "/chat", produces = "text/html;charset=UTF-8")
    public Flux<String> chat(@RequestParam("message") String message,
                             @RequestParam("moduleType") String moduleType,
                             @RequestParam(value = "sessionId", required = false) String sessionId,
                             @RequestParam(value = "memoryId", required = false) String legacyMemoryId) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || currentUser.getId() == null) {
            throw new RuntimeException("未登录或登录已失效");
        }
        String effectiveSessionId = sessionId;
        if (!StringUtils.hasText(effectiveSessionId)) {
            effectiveSessionId = legacyMemoryId;
        }
        ModuleType targetModule = ModuleType.fromCode(moduleType);
        return chatGatewayService.chat(currentUser.getId(), targetModule, effectiveSessionId, message);
    }
}
