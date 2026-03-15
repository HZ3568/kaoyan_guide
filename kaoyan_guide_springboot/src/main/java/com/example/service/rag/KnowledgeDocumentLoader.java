package com.example.service.rag;

import cn.hutool.core.io.FileUtil;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Component;

import java.io.File;
import java.nio.charset.StandardCharsets;

@Component
public class KnowledgeDocumentLoader {

    public String loadAsText(String filePath, String fileType) {
        String normalizedType = normalizeFileType(fileType);
        if ("pdf".equals(normalizedType)) {
            return loadPdf(filePath);
        }
        if ("txt".equals(normalizedType) || "md".equals(normalizedType)) {
            return FileUtil.readString(new File(filePath), StandardCharsets.UTF_8);
        }
        throw new IllegalArgumentException("暂不支持的文件类型：" + fileType);
    }

    private String loadPdf(String filePath) {
        try (PDDocument document = PDDocument.load(new File(filePath))) {
            return new PDFTextStripper().getText(document);
        } catch (Exception e) {
            throw new RuntimeException("PDF解析失败: " + e.getMessage());
        }
    }

    private String normalizeFileType(String fileType) {
        if (fileType == null) {
            return "";
        }
        return fileType.trim().toLowerCase();
    }
}
