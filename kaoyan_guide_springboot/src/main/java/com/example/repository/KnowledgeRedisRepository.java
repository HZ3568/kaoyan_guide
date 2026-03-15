package com.example.repository;

import com.example.entity.KbFile;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Repository;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

@Repository
public class KnowledgeRedisRepository {

    private final StringRedisTemplate redisTemplate;

    public KnowledgeRedisRepository(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public String buildFilePrefix(Long fileId) {
        return "kb:file:" + fileId;
    }

    public String buildMetaKey(Long fileId) {
        return buildFilePrefix(fileId) + ":meta";
    }

    public String buildIndexKey(Long fileId) {
        return buildFilePrefix(fileId) + ":keys";
    }

    public String buildEmbeddingKey(Long fileId, Integer segmentNo) {
        return buildFilePrefix(fileId) + ":embedding:" + segmentNo;
    }

    public void saveFileMeta(KbFile file) {
        String metaKey = buildMetaKey(file.getId());
        Map<String, String> meta = new HashMap<>();
        meta.put("fileId", String.valueOf(file.getId()));
        meta.put("fileName", safe(file.getFileName()));
        meta.put("fileHash", safe(file.getFileHash()));
        meta.put("status", safe(file.getStatus()));
        meta.put("redisPrefix", safe(file.getRedisPrefix()));
        redisTemplate.opsForHash().putAll(metaKey, meta);
        redisTemplate.opsForSet().add(buildIndexKey(file.getId()), metaKey);
    }

    public void saveEmbeddingMapping(Long fileId, Integer segmentNo, String vectorId) {
        String embeddingKey = buildEmbeddingKey(fileId, segmentNo);
        redisTemplate.opsForValue().set(embeddingKey, safe(vectorId));
        redisTemplate.opsForSet().add(buildIndexKey(fileId), embeddingKey);
    }

    public Set<String> getTrackedKeys(Long fileId) {
        return redisTemplate.opsForSet().members(buildIndexKey(fileId));
    }

    public String getStringValue(String key) {
        return redisTemplate.opsForValue().get(key);
    }

    public void deleteKeys(Collection<String> keys) {
        if (keys == null || keys.isEmpty()) {
            return;
        }
        redisTemplate.delete(keys);
    }

    public void deleteIndexKey(Long fileId) {
        redisTemplate.delete(buildIndexKey(fileId));
    }

    public void clearFileTracking(Long fileId) {
        Set<String> keys = getTrackedKeys(fileId);
        deleteKeys(keys);
        deleteIndexKey(fileId);
    }

    private String safe(String value) {
        return value == null ? "" : value;
    }
}
