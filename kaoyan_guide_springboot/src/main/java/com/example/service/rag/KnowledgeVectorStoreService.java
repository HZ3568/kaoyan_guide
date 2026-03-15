package com.example.service.rag;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.filter.comparison.IsEqualTo;
import jakarta.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class KnowledgeVectorStoreService {

    private static final Logger log = LoggerFactory.getLogger(KnowledgeVectorStoreService.class);

    @Resource
    private EmbeddingModel embeddingModel;

    @Resource
    private EmbeddingStore<TextSegment> embeddingStore;

    public int ingest(Long documentId, List<TextSegment> segments) {
        if (segments == null || segments.isEmpty()) {
            return 0;
        }
        for (TextSegment segment : segments) {
            embeddingStore.add(embeddingModel.embed(segment).content(), segment);
        }
        return segments.size();
    }

    public void removeByDocumentId(Long documentId) {
        if (documentId == null) {
            return;
        }
        try {
            embeddingStore.removeAll(new IsEqualTo("documentId", String.valueOf(documentId)));
        } catch (Exception e) {
            String message = e.getMessage();
            if (message != null && message.contains("wrong number of arguments for 'del' command")) {
                log.warn("删除知识库向量时未找到可删数据，documentId={}", documentId);
                return;
            }
            throw e;
        }
    }
}
