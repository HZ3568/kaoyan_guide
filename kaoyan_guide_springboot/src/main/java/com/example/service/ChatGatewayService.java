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

    private List<String> resolveSelectedTools(ModuleType moduleType) {
        if (moduleType == ModuleType.LEARNING_PLAN) {
            return List.of();
        }
        return conversationContextService.getTools(moduleType);
    }

    private Flux<String> sanitizeResponse(Flux<String> rawResponse) {
        return rawResponse.collectList()
                .map(chunks -> String.join("", chunks))
                .map(chatOutputSanitizer::sanitize)
                .flatMapMany(Flux::just);
    }
}
