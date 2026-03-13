package com.example.service;

import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.request.ChatRequest;
import dev.langchain4j.model.chat.response.ChatResponse;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import reactor.core.publisher.Flux;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

@Service
public class LearningPlanChatService {
    private final ChatModel openAiChatModel;
    private final String systemPrompt;

    /**
     * 初始化学习规划聊天服务，并预加载系统提示词。
     */
    public LearningPlanChatService(@Qualifier("openAiChatModel") ChatModel openAiChatModel) {
        this.openAiChatModel = openAiChatModel;
        this.systemPrompt = loadSystemPrompt();
    }

    /**
     * 学习规划模块对话入口。
     * 当前为单轮调用：每次仅拼接系统提示词 + 本轮用户消息，不读取历史记忆。
     */
    public Flux<String> chat(String sessionId, String message) {
        List<ChatMessage> messages = new ArrayList<>();
        if (StringUtils.hasText(systemPrompt)) {
            messages.add(SystemMessage.from(systemPrompt));
        }
        messages.add(UserMessage.from(message));
        ChatRequest request = ChatRequest.builder()
                .messages(messages)
                .build();
        ChatResponse response = openAiChatModel.chat(request);
        if (response == null || response.aiMessage() == null || response.aiMessage().text() == null) {
            return Flux.just("");
        }
        return Flux.just(response.aiMessage().text());
    }

    /**
     * 从类路径加载学习规划系统提示词。
     * 文件不存在或读取失败时返回空串，保证服务可降级运行。
     */
    private String loadSystemPrompt() {
        ClassPathResource resource = new ClassPathResource("prompts/learning_plan_system_prompt.txt");
        if (!resource.exists()) {
            return "";
        }
        try {
            byte[] bytes = resource.getInputStream().readAllBytes();
            return new String(bytes, StandardCharsets.UTF_8).trim();
        } catch (IOException e) {
            return "";
        }
    }
}
