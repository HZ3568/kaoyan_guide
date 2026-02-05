package com.example.common.config;

import dev.langchain4j.community.store.embedding.redis.RedisEmbeddingStore;
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.DocumentSplitter;
import dev.langchain4j.data.document.loader.FileSystemDocumentLoader;
import dev.langchain4j.data.document.parser.apache.pdfbox.ApachePdfBoxDocumentParser;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.memory.ChatMemory;
import dev.langchain4j.memory.chat.ChatMemoryProvider;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.memory.chat.ChatMemoryStore;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class CommonConfig {

    @Autowired
    private ChatMemoryStore redisChatMemoryStore;
    @Autowired
    private EmbeddingModel embeddingModel;
    @Autowired
    private RedisEmbeddingStore redisEmbeddingStore;

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

    // 构建向量数据库操作对象
//    @Bean
    public EmbeddingStore store() {
        // 1. 加载文档
        List<Document> documents = FileSystemDocumentLoader.loadDocuments("D:\\1_code\\Java\\consultant\\src\\main\\resources\\content", new ApachePdfBoxDocumentParser());

        // 2. 构建向量数据库操作对象
        // InMemoryEmbeddingStore store = new InMemoryEmbeddingStore();


        // 3. 构建文档分割器对象
        DocumentSplitter ds = DocumentSplitters.recursive(500, 100);

        // 3. 构建一个EmbeddingStoreIngestor对象，完成文本的切割、向量化和存储
        EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
                .embeddingStore(redisEmbeddingStore)
                .documentSplitter(ds)
                .embeddingModel(embeddingModel)
                .build();
        ingestor.ingest(documents);
        return redisEmbeddingStore;
    }


    // 构建向量数据库检索对象
    @Bean
    public ContentRetriever contentRetriever() {
        return EmbeddingStoreContentRetriever.builder()
                .embeddingStore(redisEmbeddingStore)
                .embeddingModel(embeddingModel)
                .minScore(0.5)
                .maxResults(3)
                .build();
    }
}