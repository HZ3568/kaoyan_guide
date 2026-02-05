package com.example.service;

import dev.langchain4j.service.MemoryId;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.spring.AiService;
import dev.langchain4j.service.spring.AiServiceWiringMode;
import reactor.core.publisher.Flux;

@AiService(
        wiringMode = AiServiceWiringMode.EXPLICIT, // 手动装配
        chatModel = "openAiChatModel", // 指定模型
        streamingChatModel = "openAiStreamingChatModel",
        chatMemory = "chatMemory", // 配置会话记忆对象
        chatMemoryProvider = "chatMemoryProvider", // 配置会话记忆提供者对象
        contentRetriever = "contentRetriever", // 配置向量数据库检索器对象
        tools = "reservationTool"
)
//@AiService
// 注解+接口：动态生成实现类
public interface ChatService {
    // @SystemMessage("你是我的女朋友！")
    @SystemMessage(fromResource = "system.txt")
    public Flux<String> chat(@MemoryId String memoryId, @UserMessage String message);
}
