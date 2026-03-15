package com.example.service.rag.impl;

import com.example.entity.KnowledgeDocument;
import com.example.mapper.KnowledgeDocumentMapper;
import com.example.service.rag.KnowledgeDocumentLoader;
import com.example.service.rag.KnowledgeDocumentSplitter;
import com.example.service.rag.KnowledgeIngestService;
import com.example.service.rag.KnowledgeVectorStoreService;
import dev.langchain4j.data.segment.TextSegment;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class KnowledgeIngestServiceImpl implements KnowledgeIngestService {

    private static final String STATUS_PROCESSING = "PROCESSING";
    private static final String STATUS_SUCCESS = "SUCCESS";
    private static final String STATUS_FAILED = "FAILED";

    @Resource
    private KnowledgeDocumentMapper knowledgeDocumentMapper;

    @Resource
    private KnowledgeDocumentLoader knowledgeDocumentLoader;

    @Resource
    private KnowledgeDocumentSplitter knowledgeDocumentSplitter;

    @Resource
    private KnowledgeVectorStoreService knowledgeVectorStoreService;

    @Override
    public void ingest(KnowledgeDocument document) {
        if (document == null || document.getId() == null) {
            throw new IllegalArgumentException("知识库文档不存在");
        }
        updateStatus(document.getId(), STATUS_PROCESSING, 0, "");
        try {
            deleteDocumentVectors(document.getId());
            String text = knowledgeDocumentLoader.loadAsText(document.getFilePath(), document.getFileType());
            List<TextSegment> segments = knowledgeDocumentSplitter.split(document, text);
            int chunkCount = knowledgeVectorStoreService.ingest(document.getId(), segments);
            updateStatus(document.getId(), STATUS_SUCCESS, chunkCount, "");
        } catch (Exception e) {
            updateStatus(document.getId(), STATUS_FAILED, 0, simplifyError(e));
        }
    }

    @Override
    public void deleteDocumentVectors(Long documentId) {
        knowledgeVectorStoreService.removeByDocumentId(documentId);
    }

    private void updateStatus(Long documentId, String status, Integer chunkCount, String errorMessage) {
        KnowledgeDocument updating = new KnowledgeDocument();
        updating.setId(documentId);
        updating.setStatus(status);
        updating.setChunkCount(chunkCount);
        updating.setErrorMessage(errorMessage);
        knowledgeDocumentMapper.updateById(updating);
    }

    private String simplifyError(Exception e) {
        if (e == null) {
            return "未知错误";
        }
        String message = e.getMessage();
        if (message == null || message.isBlank()) {
            return e.getClass().getSimpleName();
        }
        return message.length() > 500 ? message.substring(0, 500) : message;
    }
}
