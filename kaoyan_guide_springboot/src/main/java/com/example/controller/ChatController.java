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

    /**
     * 统一聊天入口（SSE）。
     * 作用：
     * 1) 校验当前登录用户；
     * 2) 优先使用前端传入的 sessionId，缺失时自动生成新的 UUID；
     * 3) 回传 X-Session-Id，便于前端后续请求复用同一会话；
     * 4) 根据 moduleType 路由到对应业务模块（志愿填报 / 学习规划）。
     */
    @RequestMapping(value = "/chat", produces = "text/event-stream;charset=UTF-8")
    public Flux<String> chat(@RequestParam("message") String message,
            @RequestParam("moduleType") String moduleType,
            @RequestParam(value = "sessionId", required = false) String sessionId,
            HttpServletResponse response) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || currentUser.getId() == null) {
            throw new RuntimeException("未登录或登录已失效");
        }
        String effectiveSessionId = sessionId;
        if (!StringUtils.hasText(effectiveSessionId)) {
            effectiveSessionId = UUID.randomUUID().toString();
        }
        response.setHeader("X-Session-Id", effectiveSessionId);
        ModuleType targetModule = ModuleType.fromCode(moduleType);
        return chatGatewayService.chat(currentUser.getId(), targetModule, effectiveSessionId, message);
    }
}
