package com.example.controller;

import com.example.common.enums.ModuleType;
import com.example.entity.Account;
import com.example.service.ChatGatewayService;
import com.example.utils.TokenUtils;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import reactor.core.publisher.BaseSubscriber;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.UUID;

@RestController
public class ChatController {
    private static final Logger log = LoggerFactory.getLogger(ChatController.class);

    @Autowired
    private ChatGatewayService chatGatewayService;

    @GetMapping(value = "/chat", produces = "text/event-stream;charset=UTF-8")
    public SseEmitter chat(@RequestParam("message") String message,
                           @RequestParam("moduleType") String moduleType,
                           @RequestParam(value = "sessionId", required = false) String sessionId,
                           HttpServletResponse response) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || currentUser.getId() == null) {
            throw new RuntimeException("User is not logged in or session expired");
        }

        String effectiveSessionId = StringUtils.hasText(sessionId)
                ? sessionId
                : UUID.randomUUID().toString();

        response.setCharacterEncoding(StandardCharsets.UTF_8.name());
        response.setHeader("Cache-Control", "no-cache");
        response.setHeader("Connection", "keep-alive");
        response.setHeader("X-Accel-Buffering", "no");
        response.setHeader("X-Session-Id", effectiveSessionId);

        ModuleType targetModule = ModuleType.fromCode(moduleType);
        Integer userId = currentUser.getId();
        SseEmitter emitter = new SseEmitter(0L);

        BaseSubscriber<String> subscriber = new BaseSubscriber<>() {
            @Override
            protected void hookOnNext(String chunk) {
                String safeChunk = chunk == null ? "" : chunk;
                log.info("chat_sse_emit userId={} moduleType={} sessionId={} chunkLength={} preview={}",
                        userId,
                        targetModule.getCode(),
                        effectiveSessionId,
                        safeChunk.length(),
                        preview(safeChunk));
                try {
                    sendEvent(emitter, "message", safeChunk);
                } catch (IOException e) {
                    log.warn("chat_sse_send_failed userId={} sessionId={}", userId, effectiveSessionId, e);
                    cancel();
                    emitter.completeWithError(e);
                }
            }

            @Override
            protected void hookOnComplete() {
                try {
                    sendEvent(emitter, "done", "[DONE]");
                    emitter.complete();
                } catch (IOException e) {
                    log.warn("chat_sse_done_failed userId={} sessionId={}", userId, effectiveSessionId, e);
                    emitter.completeWithError(e);
                }
            }

            @Override
            protected void hookOnError(Throwable throwable) {
                log.error("chat_sse_error userId={} sessionId={}", userId, effectiveSessionId, throwable);
                emitter.completeWithError(throwable);
            }
        };

        emitter.onCompletion(subscriber::cancel);
        emitter.onTimeout(() -> {
            log.warn("chat_sse_timeout userId={} sessionId={}", userId, effectiveSessionId);
            subscriber.cancel();
            emitter.complete();
        });
        emitter.onError(error -> {
            log.warn("chat_sse_client_error userId={} sessionId={}", userId, effectiveSessionId, error);
            subscriber.cancel();
        });

        chatGatewayService.chat(userId, targetModule, effectiveSessionId, message)
                .subscribe(subscriber);

        return emitter;
    }

    private void sendEvent(SseEmitter emitter, String event, String data) throws IOException {
        emitter.send(SseEmitter.event()
                .name(event)
                .data(data));
    }

    private String preview(String text) {
        String compact = text.replace("\n", "\\n");
        if (compact.length() <= 120) {
            return compact;
        }
        return compact.substring(0, 120) + "...";
    }
}