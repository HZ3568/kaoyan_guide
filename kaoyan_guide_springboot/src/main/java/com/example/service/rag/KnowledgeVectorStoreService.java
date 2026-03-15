package com.example.service.rag;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.filter.comparison.IsEqualTo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class KnowledgeVectorStoreService {

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
        embeddingStore.removeAll(new IsEqualTo("documentId", String.valueOf(documentId)));
    }
}
