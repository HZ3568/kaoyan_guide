package com.example.service.rag;

import dev.langchain4j.data.document.Metadata;
import dev.langchain4j.data.segment.TextSegment;
import com.example.entity.KnowledgeDocument;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Component
public class KnowledgeDocumentSplitter {

    private static final int CHUNK_SIZE = 700;
    private static final int CHUNK_OVERLAP = 100;
    private static final Pattern SCHOOL_NAME_PATTERN = Pattern.compile("([\\u4e00-\\u9fa5]{2,}(大学|学院))");

    public List<TextSegment> split(KnowledgeDocument document, String text) {
        String normalized = normalize(text);
        if (normalized.isBlank()) {
            return List.of();
        }
        List<String> naturalBlocks = splitByNaturalStructure(normalized);
        List<TextSegment> segments = new ArrayList<>();
        String schoolName = detectSchoolName(document, normalized);
        for (String block : naturalBlocks) {
            if (block == null || block.isBlank()) {
                continue;
            }
            segments.addAll(splitLongBlock(document, schoolName, block));
        }
        return segments;
    }

    private List<String> splitByNaturalStructure(String text) {
        List<String> blocks = new ArrayList<>();
        String[] lines = text.split("\\n");
        StringBuilder currentParagraph = new StringBuilder();
        for (String line : lines) {
            String trimmed = line == null ? "" : line.trim();
            if (trimmed.isBlank()) {
                appendParagraph(blocks, currentParagraph);
                continue;
            }
            if (isHeading(trimmed)) {
                appendParagraph(blocks, currentParagraph);
                blocks.add(trimmed);
                continue;
            }
            if (!currentParagraph.isEmpty()) {
                currentParagraph.append('\n');
            }
            currentParagraph.append(trimmed);
        }
        appendParagraph(blocks, currentParagraph);
        return blocks;
    }

    private void appendParagraph(List<String> blocks, StringBuilder paragraph) {
        if (paragraph.isEmpty()) {
            return;
        }
        blocks.add(paragraph.toString().trim());
        paragraph.setLength(0);
    }

    private boolean isHeading(String line) {
        return line.startsWith("#")
                || line.matches("^第[一二三四五六七八九十百千0-9]+[章节部分篇].*")
                || line.matches("^[0-9一二三四五六七八九十]+[.、）)].*");
    }

    private List<TextSegment> splitLongBlock(KnowledgeDocument document, String schoolName, String block) {
        List<TextSegment> segments = new ArrayList<>();
        int start = 0;
        int length = block.length();
        while (start < length) {
            int end = Math.min(start + CHUNK_SIZE, length);
            String chunk = block.substring(start, end).trim();
            if (!chunk.isBlank()) {
                segments.add(TextSegment.from(chunk, buildMetadata(document, schoolName)));
            }
            if (end >= length) {
                break;
            }
            start = Math.max(0, end - CHUNK_OVERLAP);
        }
        return segments;
    }

    private Metadata buildMetadata(KnowledgeDocument document, String schoolName) {
        Metadata metadata = new Metadata();
        metadata.put("documentId", String.valueOf(document.getId()));
        metadata.put("title", safe(document.getTitle()));
        metadata.put("businessType", safe(document.getBusinessType()));
        metadata.put("fileName", safe(document.getFileName()));
        if (!schoolName.isBlank()) {
            metadata.put("schoolName", schoolName);
        }
        return metadata;
    }

    private String detectSchoolName(KnowledgeDocument document, String text) {
        String fromTitle = extractSchoolName(document.getTitle());
        if (!fromTitle.isBlank()) {
            return fromTitle;
        }
        return extractSchoolName(text);
    }

    private String extractSchoolName(String text) {
        if (text == null || text.isBlank()) {
            return "";
        }
        Matcher matcher = SCHOOL_NAME_PATTERN.matcher(text);
        if (matcher.find()) {
            return matcher.group(1);
        }
        return "";
    }

    private String normalize(String text) {
        if (text == null) {
            return "";
        }
        return text.replace("\r\n", "\n").replace('\r', '\n').trim();
    }

    private String safe(String value) {
        return value == null ? "" : value;
    }
}
