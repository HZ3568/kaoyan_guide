package com.example.common.config;

import dev.langchain4j.memory.ChatMemory;
import dev.langchain4j.memory.chat.ChatMemoryProvider;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.store.memory.chat.ChatMemoryStore;
import com.example.service.rag.SchoolAwareContentRetriever;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.data.segment.TextSegment;

@Configuration
public class CommonConfig {

    @Autowired
    private ChatMemoryStore redisChatMemoryStore;
    @Autowired
    private EmbeddingModel embeddingModel;
    @Autowired
    private EmbeddingStore<TextSegment> embeddingStore;

    // 构建会话记忆对象
    @Bean
    public ChatMemory chatMemory() {
        MessageWindowChatMemory memory = MessageWindowChatMemory.builder()
                .maxMessages(20)
                .build();
        return memory;  //  将创建的 MessageWindowChatMemory 实例返回。Spring 容器会接收这个实例，并将其注册为一个名为 chatMemory 的 Bean，类型为 ChatMemory
    }

    // 构建ChatMemoryProvider对象
    @Bean
    public ChatMemoryProvider chatMemoryProvider() {
        ChatMemoryProvider provider = new ChatMemoryProvider() {
            @Override
            public ChatMemory get(Object MemoryId) {
                return MessageWindowChatMemory.builder()
                        .id(MemoryId)
                        .maxMessages(20)
                        .chatMemoryStore(redisChatMemoryStore)
                        .build();
            }
        };
        return provider;
    }

    // 构建向量数据库检索对象
    @Bean
    public ContentRetriever contentRetriever() {
        return new SchoolAwareContentRetriever(
                embeddingStore,
                embeddingModel,
                0.4,
                8,
                3);
    }
}
