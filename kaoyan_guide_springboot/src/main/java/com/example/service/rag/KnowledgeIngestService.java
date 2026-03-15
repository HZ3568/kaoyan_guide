package com.example.service.rag;

import com.example.entity.KnowledgeDocument;

public interface KnowledgeIngestService {

    void ingest(KnowledgeDocument document);

    void deleteDocumentVectors(Long documentId);
}
