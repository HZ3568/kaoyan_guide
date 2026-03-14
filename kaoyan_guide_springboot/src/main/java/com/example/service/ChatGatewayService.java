package com.example.service;

import com.example.common.enums.ModuleType;
import com.example.entity.SessionContext;
import com.example.service.chat.ChatOutputSanitizer;
import com.example.service.chat.ConversationContextService;
import com.example.service.chat.PromptAssembly;
import com.example.service.chat.PromptBuilder;
import com.example.utils.MemoryKeyBuilder;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.store.memory.chat.ChatMemoryStore;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

import java.util.Collections;
import java.util.List;

@Service
public class ChatGatewayService {
    private static final Logger log = LoggerFactory.getLogger(ChatGatewayService.class);

    private final ChatService volunteerApplyChatService;
    private final LearningPlanChatService learningPlanChatService;
    private final ConversationContextService conversationContextService;
    private final PromptBuilder promptBuilder;
    private final ChatOutputSanitizer chatOutputSanitizer;
    private final MemoryKeyBuilder memoryKeyBuilder;
    private final ChatMemoryStore chatMemoryStore;

    /**
     * 构造聊天网关，注入模块路由与上下文组装所需依赖。
     */
    public ChatGatewayService(ChatService volunteerApplyChatService,
            LearningPlanChatService learningPlanChatService,
            ConversationContextService conversationContextService,
            PromptBuilder promptBuilder,
            ChatOutputSanitizer chatOutputSanitizer,
            MemoryKeyBuilder memoryKeyBuilder,
            ChatMemoryStore chatMemoryStore) {
        this.volunteerApplyChatService = volunteerApplyChatService;
        this.learningPlanChatService = learningPlanChatService;
        this.conversationContextService = conversationContextService;
        this.promptBuilder = promptBuilder;
        this.chatOutputSanitizer = chatOutputSanitizer;
        this.memoryKeyBuilder = memoryKeyBuilder;
        this.chatMemoryStore = chatMemoryStore;
    }

    /**
     * 聊天网关主入口。
     * 核心流程：
     * 1) 组装 memoryId 与会话上下文；
     * 2) 按模块决定是否读取历史消息（仅志愿填报启用记忆）；
     * 3) 解析提示词、工具与是否启用 RAG；
     * 4) 分发到对应模块服务；
     * 5) 对模型输出进行统一清洗后返回。
     */
    public Flux<String> chat(Integer userId, ModuleType moduleType, String sessionId, String message) {
        String memoryId = memoryKeyBuilder.build(userId, moduleType, sessionId);
        SessionContext sessionContext = new SessionContext(userId, moduleType, sessionId, memoryId);
        boolean useMemory = moduleType == ModuleType.VOLUNTEER_APPLY;
        List<ChatMessage> historyMessages = useMemory ? readHistory(memoryId) : Collections.emptyList();
        String promptResource = conversationContextService.getPromptResource(moduleType);
        List<String> toolNames = resolveSelectedTools(moduleType);
        boolean includeRag = conversationContextService.isRagEnabled(moduleType);
        PromptAssembly promptAssembly = promptBuilder.build(historyMessages.size(), includeRag, toolNames,
                promptResource);

        log.info(
                "chat_context moduleType={} userId={} sessionId={} memoryId={} selectedTools={} contextParts={} finalPromptSource={} messageCount={} whetherUseMemory={} retrievalEnabled={}",
                sessionContext.getModuleType().getCode(),
                sessionContext.getUserId(),
                sessionContext.getSessionId(),
                sessionContext.getMemoryKey(),
                toolNames,
                promptAssembly.getContextParts(),
                promptAssembly.getFinalPromptSource(),
                promptAssembly.getMessageCount(),
                useMemory,
                includeRag);

        Flux<String> rawResponse = switch (moduleType) {
            case LEARNING_PLAN -> learningPlanChatService.chat(sessionContext.getSessionId(), message);
            case VOLUNTEER_APPLY -> volunteerApplyChatService.chat(memoryId, message);
        };
        return sanitizeResponse(rawResponse);
    }

    /**
     * 从持久化记忆中读取历史消息。
     * 读取失败时降级为空历史，避免影响本次对话可用性。
     */
    private List<ChatMessage> readHistory(String memoryKey) {
        try {
            List<ChatMessage> messages = chatMemoryStore.getMessages(memoryKey);
            if (messages == null) {
                return Collections.emptyList();
            }
            return messages;
        } catch (Exception e) {
            log.warn("读取历史消息失败 memoryKey={}", memoryKey, e);
            return Collections.emptyList();
        }
    }

    /**
     * 按模块解析可用工具列表。
     * 学习规划模块显式禁用工具，避免误触发志愿填报工具调用。
     */
    private List<String> resolveSelectedTools(ModuleType moduleType) {
        if (moduleType == ModuleType.LEARNING_PLAN) {
            return List.of();
        }
        return conversationContextService.getTools(moduleType);
    }

    /**
     * 对流式分片做轻量清洗并直接透传，避免提前聚合导致前端无法实时渲染。
     */
    private Flux<String> sanitizeResponse(Flux<String> rawResponse) {
        return rawResponse
                .map(this::sanitizeChunk)
                .doOnNext(chunk -> log.info("chat_gateway_chunk length={} preview={}", chunk.length(), preview(chunk)));
    }

    private String sanitizeChunk(String chunk) {
        if (chunk == null) {
            return "";
        }
        String trimmed = chunk.trim();
        if ((trimmed.startsWith("{") && trimmed.endsWith("}"))
                || (trimmed.startsWith("```") && trimmed.endsWith("```"))) {
            return chatOutputSanitizer.sanitize(chunk);
        }
        return chunk;
    }

    private String preview(String text) {
        if (text == null) {
            return "";
        }
        String compact = text.replace("\n", "\\n");
        int max = 120;
        if (compact.length() <= max) {
            return compact;
        }
        return compact.substring(0, max) + "...";
    }
}
