package com.example.service;

import dev.langchain4j.service.MemoryId;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.spring.AiService;
import dev.langchain4j.service.spring.AiServiceWiringMode;
import reactor.core.publisher.Flux;

@AiService(
        wiringMode = AiServiceWiringMode.EXPLICIT,
        chatModel = "openAiChatModel",
        streamingChatModel = "openAiStreamingChatModel",
        chatMemory = "chatMemory",
        chatMemoryProvider = "chatMemoryProvider",
        contentRetriever = "contentRetriever",
        tools = "schoolCompareTool"
)
public interface ChatService {
    /**
     * 考研院校咨询模块对话入口。
     * memoryId 用于隔离用户在该模块下的会话记忆；
     * message 为本轮用户输入，返回流式模型输出。
     */
    @SystemMessage(fromResource = "prompts/consult-college-system-prompt.txt")
    Flux<String> chat(@MemoryId String memoryId, @UserMessage String message);
}
