package com.example.service.rag;

import com.example.entity.KbContent;
import com.example.entity.KbFile;
import com.example.repository.KnowledgeRedisRepository;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.filter.comparison.IsEqualTo;
import jakarta.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

@Component
public class KnowledgeVectorStoreService {

    private static final Logger log = LoggerFactory.getLogger(KnowledgeVectorStoreService.class);

    @Resource
    private EmbeddingModel embeddingModel;

    @Resource
    private EmbeddingStore<TextSegment> embeddingStore;

    @Resource
    private KnowledgeDocumentSplitter knowledgeDocumentSplitter;

    @Resource
    private KnowledgeRedisRepository knowledgeRedisRepository;

    public int ingest(KbFile file, List<KbContent> contents) {
        if (file == null || file.getId() == null || contents == null || contents.isEmpty()) {
            return 0;
        }
        String schoolName = knowledgeDocumentSplitter.detectSchoolName(file, file.getTitle());
        for (KbContent content : contents) {
            TextSegment segment = knowledgeDocumentSplitter.buildSegment(file, content, schoolName);
            String vectorId = embeddingStore.add(embeddingModel.embed(segment).content(), segment);
            knowledgeRedisRepository.saveEmbeddingMapping(file.getId(), content.getSegmentNo(), vectorId);
        }
        return contents.size();
    }

    public boolean removeByFileId(Long fileId) {
        if (fileId == null) {
            return true;
        }
        Set<String> trackedKeys = knowledgeRedisRepository.getTrackedKeys(fileId);
        if (trackedKeys == null || trackedKeys.isEmpty()) {
            return removeByDocumentIdFallback(fileId);
        }
        Set<String> deleteKeys = new LinkedHashSet<>(trackedKeys);
        deleteKeys.add(knowledgeRedisRepository.buildIndexKey(fileId));
        List<String> vectorIds = new ArrayList<>();
        for (String key : trackedKeys) {
            if (key != null && key.contains(":embedding:")) {
                String vectorId = knowledgeRedisRepository.getStringValue(key);
                if (StringUtils.hasText(vectorId)) {
                    vectorIds.add(vectorId);
                }
            }
        }
        for (String vectorId : vectorIds) {
            embeddingStore.remove(vectorId);
        }
        knowledgeRedisRepository.deleteKeys(deleteKeys);
        return true;
    }

    private boolean removeByDocumentIdFallback(Long documentId) {
        if (documentId == null) {
            return true;
        }
        try {
            embeddingStore.removeAll(new IsEqualTo("documentId", String.valueOf(documentId)));
            knowledgeRedisRepository.clearFileTracking(documentId);
            return true;
        } catch (Exception e) {
            String message = e.getMessage();
            if (message != null && message.contains("wrong number of arguments for 'del' command")) {
                log.warn("删除知识库向量时未找到可删数据，documentId={}", documentId);
                knowledgeRedisRepository.clearFileTracking(documentId);
                return true;
            }
            throw e;
        }
    }
}
