package com.example.service.rag;

import com.example.entity.KbFile;

public interface KnowledgeIngestService {

    void ingest(KbFile file);

    boolean deleteFileVectors(Long fileId);
}
