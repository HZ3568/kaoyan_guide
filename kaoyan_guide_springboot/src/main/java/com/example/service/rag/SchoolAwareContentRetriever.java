package com.example.service.rag;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.rag.content.Content;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.rag.query.Query;
import dev.langchain4j.store.embedding.EmbeddingStore;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SchoolAwareContentRetriever implements ContentRetriever {

    private static final Logger log = LoggerFactory.getLogger(SchoolAwareContentRetriever.class);
    private static final Pattern SCHOOL_NAME_PATTERN = Pattern.compile("([\\u4e00-\\u9fa5]{2,}(大学|学院))");
    private static final Set<String> SCHOOL_INFO_QUERY_KEYWORDS = Set.of(
            "学校信息", "学校介绍", "学校简介", "院校介绍", "院校简介", "学校概况", "院校概况", "基本情况", "学校情况", "了解");
    private static final Set<String> SCHOOL_INFO_CHUNK_KEYWORDS = Set.of(
            "学校简介", "院校简介", "学校概况", "院校概况", "学校介绍", "院校介绍", "基本情况", "办学层次", "主管部门", "办学性质", "历史沿革");
    private static final Set<String> ADMISSION_CHUNK_KEYWORDS = Set.of(
            "分专业录取", "录取情况", "录取分数", "最低分", "最高分", "位次", "招生计划", "中外合作办学", "分数线");
    private static final Map<String, String> SCHOOL_ALIAS_MAP = Map.of(
            "西工大", "西北工业大学",
            "西电", "西安电子科技大学",
            "北理工", "北京理工大学");

    private final ContentRetriever delegate;
    private final int finalMaxResults;

    public SchoolAwareContentRetriever(EmbeddingStore<TextSegment> embeddingStore, EmbeddingModel embeddingModel,
                                       double minScore, int retrieveMaxResults, int finalMaxResults) {
        this.delegate = EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
                .minScore(minScore)
                .maxResults(retrieveMaxResults)
                .build();
        this.finalMaxResults = finalMaxResults;
    }

    @Override
    public List<Content> retrieve(Query query) {
        String rawQuery = query == null || query.text() == null ? "" : query.text();
        String normalizedQuery = normalize(rawQuery);
        String detectedSchoolName = detectSchoolName(rawQuery, normalizedQuery);
        String detectedIntent = detectIntent(normalizedQuery);

        List<Content> retrievedContents = delegate.retrieve(query);
        int retrievedChunkCount = retrievedContents.size();

        List<Content> filteredContents = filterBySchoolName(retrievedContents, detectedSchoolName);
        int filteredChunkCount = filteredContents.size();

        List<Content> deduplicatedContents = deduplicate(filteredContents);
        int deduplicatedChunkCount = deduplicatedContents.size();

        List<Content> rerankedContents = rerankByIntent(deduplicatedContents, detectedIntent, detectedSchoolName);
        List<Content> finalContents = limit(rerankedContents, finalMaxResults);
        String finalInjectedContextPreview = buildPreview(finalContents);

        log.info(
                "rag_retrieval normalizedQuery={} detectedSchoolName={} detectedIntent={} retrievedChunkCount={} filteredChunkCount={} deduplicatedChunkCount={} finalInjectedContextPreview={}",
                normalizedQuery,
                detectedSchoolName,
                detectedIntent,
                retrievedChunkCount,
                filteredChunkCount,
                deduplicatedChunkCount,
                finalInjectedContextPreview);
        return finalContents;
    }

    private List<Content> filterBySchoolName(List<Content> contents, String schoolName) {
        if (schoolName == null || schoolName.isBlank()) {
            return contents;
        }
        String normalizedSchoolName = normalize(schoolName);
        List<Content> filtered = new ArrayList<>();
        for (Content content : contents) {
            String text = extractText(content);
            if (normalize(text).contains(normalizedSchoolName)) {
                filtered.add(content);
            }
        }
        return filtered;
    }

    private List<Content> deduplicate(List<Content> contents) {
        Map<String, Content> unique = new LinkedHashMap<>();
        for (Content content : contents) {
            String key = normalize(extractText(content));
            if (key.isBlank()) {
                continue;
            }
            unique.putIfAbsent(key, content);
        }
        return new ArrayList<>(unique.values());
    }

    private List<Content> rerankByIntent(List<Content> contents, String intent, String schoolName) {
        if (!"SCHOOL_INFO".equals(intent)) {
            return contents;
        }
        String normalizedSchoolName = normalize(schoolName);
        List<ContentWithScore> scoredContents = new ArrayList<>();
        for (Content content : contents) {
            String text = extractText(content);
            String normalizedText = normalize(text);
            int score = 0;
            if (!normalizedSchoolName.isBlank() && normalizedText.contains(normalizedSchoolName)) {
                score += 4;
            }
            for (String keyword : SCHOOL_INFO_CHUNK_KEYWORDS) {
                if (text.contains(keyword)) {
                    score += 2;
                }
            }
            for (String keyword : ADMISSION_CHUNK_KEYWORDS) {
                if (text.contains(keyword)) {
                    score -= 2;
                }
            }
            scoredContents.add(new ContentWithScore(content, score));
        }
        scoredContents.sort((left, right) -> Integer.compare(right.score, left.score));
        List<Content> reranked = new ArrayList<>();
        for (ContentWithScore item : scoredContents) {
            reranked.add(item.content);
        }
        return reranked;
    }

    private String detectSchoolName(String rawQuery, String normalizedQuery) {
        for (Map.Entry<String, String> entry : SCHOOL_ALIAS_MAP.entrySet()) {
            if (normalizedQuery.contains(normalize(entry.getKey()))) {
                return entry.getValue();
            }
        }
        Matcher matcher = SCHOOL_NAME_PATTERN.matcher(rawQuery);
        if (matcher.find()) {
            return matcher.group(1);
        }
        return "";
    }

    private String detectIntent(String normalizedQuery) {
        for (String keyword : SCHOOL_INFO_QUERY_KEYWORDS) {
            if (normalizedQuery.contains(normalize(keyword))) {
                return "SCHOOL_INFO";
            }
        }
        return "GENERAL";
    }

    private List<Content> limit(List<Content> contents, int maxResults) {
        if (contents.size() <= maxResults) {
            return contents;
        }
        return new ArrayList<>(contents.subList(0, maxResults));
    }

    private String buildPreview(List<Content> contents) {
        StringBuilder builder = new StringBuilder();
        Set<String> seen = new LinkedHashSet<>();
        for (Content content : contents) {
            String text = extractText(content).replaceAll("\\s+", " ").trim();
            if (text.isBlank() || seen.contains(text)) {
                continue;
            }
            seen.add(text);
            if (builder.length() > 0) {
                builder.append(" | ");
            }
            builder.append(text);
            if (builder.length() >= 500) {
                break;
            }
        }
        String preview = builder.toString();
        if (preview.length() > 500) {
            return preview.substring(0, 500);
        }
        return preview;
    }

    private String extractText(Content content) {
        if (content == null || content.textSegment() == null || content.textSegment().text() == null) {
            return "";
        }
        return content.textSegment().text();
    }

    private String normalize(String text) {
        if (text == null) {
            return "";
        }
        return text.replaceAll("[\\s\\p{Punct}，。！？、：；“”‘’（）《》【】·]", "")
                .toLowerCase();
    }

    private static class ContentWithScore {
        private final Content content;
        private final int score;

        private ContentWithScore(Content content, int score) {
            this.content = content;
            this.score = score;
        }
    }
}
