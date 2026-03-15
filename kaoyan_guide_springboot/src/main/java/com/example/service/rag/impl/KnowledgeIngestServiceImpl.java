package com.example.service.rag.impl;

import com.example.entity.KbContent;
import com.example.entity.KbFile;
import com.example.mapper.KbContentMapper;
import com.example.mapper.KbFileMapper;
import com.example.repository.KnowledgeRedisRepository;
import com.example.service.rag.KnowledgeDocumentLoader;
import com.example.service.rag.KnowledgeDocumentSplitter;
import com.example.service.rag.KnowledgeIngestService;
import com.example.service.rag.KnowledgeVectorStoreService;
import jakarta.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class KnowledgeIngestServiceImpl implements KnowledgeIngestService {

    private static final Logger log = LoggerFactory.getLogger(KnowledgeIngestServiceImpl.class);
    private static final String STATUS_PROCESSING = "PROCESSING";
    private static final String STATUS_PARSED = "PARSED";
    private static final String STATUS_INDEXED = "INDEXED";
    private static final String STATUS_FAILED = "FAILED";

    @Resource
    private KbFileMapper kbFileMapper;

    @Resource
    private KbContentMapper kbContentMapper;

    @Resource
    private KnowledgeDocumentLoader knowledgeDocumentLoader;

    @Resource
    private KnowledgeDocumentSplitter knowledgeDocumentSplitter;

    @Resource
    private KnowledgeVectorStoreService knowledgeVectorStoreService;

    @Resource
    private KnowledgeRedisRepository knowledgeRedisRepository;

    @Override
    public void ingest(KbFile file) {
        if (file == null || file.getId() == null) {
            throw new IllegalArgumentException("知识库文档不存在");
        }
        updateStatus(file.getId(), STATUS_PROCESSING, 0, "");
        try {
            String text = knowledgeDocumentLoader.loadAsText(file.getFilePath(), file.getFileType());
            List<KbContent> contents = knowledgeDocumentSplitter.split(file, text);
            kbContentMapper.deleteByFileId(file.getId());
            if (!contents.isEmpty()) {
                kbContentMapper.insertBatch(contents);
            }
            updateStatus(file.getId(), STATUS_PARSED, contents.size(), "");
            int segmentCount = knowledgeVectorStoreService.ingest(file, contents);
            updateStatus(file.getId(), STATUS_INDEXED, segmentCount, "");
        } catch (Exception e) {
            log.error("知识库文档入库失败，fileId={}", file.getId(), e);
            try {
                knowledgeVectorStoreService.removeByFileId(file.getId());
            } catch (Exception cleanupError) {
                log.error("清理失败文件Redis向量失败，fileId={}", file.getId(), cleanupError);
            }
            updateStatus(file.getId(), STATUS_FAILED, 0, simplifyError(e));
        }
    }

    @Override
    public boolean deleteFileVectors(Long fileId) {
        return knowledgeVectorStoreService.removeByFileId(fileId);
    }

    private void updateStatus(Long fileId, String status, Integer segmentCount, String errorMessage) {
        KbFile updating = new KbFile();
        updating.setId(fileId);
        updating.setStatus(status);
        updating.setSegmentCount(segmentCount);
        updating.setErrorMessage(errorMessage);
        kbFileMapper.updateById(updating);
        KbFile latest = kbFileMapper.selectById(fileId);
        if (latest != null) {
            knowledgeRedisRepository.saveFileMeta(latest);
        }
    }

    private String simplifyError(Exception e) {
        if (e == null) {
            return "未知错误";
        }
        String message = e.getMessage();
        if (message == null || message.isBlank()) {
            return e.getClass().getSimpleName();
        }
        String normalized = message.replace("\r", " ").replace("\n", " ").trim();
        if (normalized.length() > 200) {
            normalized = normalized.substring(0, 200);
        }
        return normalized;
    }
}
