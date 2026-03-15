package com.example.repository;

import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.ChatMessageDeserializer;
import dev.langchain4j.data.message.ChatMessageSerializer;
import dev.langchain4j.store.memory.chat.ChatMemoryStore;
import com.example.utils.MemoryKeyBuilder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Repository;
import org.springframework.util.StringUtils;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;

@Repository
public class RedisChatMemoryStore implements ChatMemoryStore {

    private final StringRedisTemplate redisTemplate;
    private final MemoryKeyBuilder memoryKeyBuilder;

    @Value("${app.chat.memory.ttl-days:7}")
    private long memoryTtlDays;

    public RedisChatMemoryStore(StringRedisTemplate redisTemplate, MemoryKeyBuilder memoryKeyBuilder) {
        this.redisTemplate = redisTemplate;
        this.memoryKeyBuilder = memoryKeyBuilder;
    }

    @Override
    public List<ChatMessage> getMessages(Object memoryId) {
        String currentMemoryId = memoryId.toString();
        String json = redisTemplate.opsForValue().get(memoryKeyBuilder.toRedisKey(currentMemoryId));
        if (!StringUtils.hasText(json)) {
            return Collections.emptyList();
        }
        if (json.trim().startsWith("[")) {
            return ChatMessageDeserializer.messagesFromJson(json);
        }
        try {
            JSONObject payload = JSONUtil.parseObj(json);
            String messagesJson = payload.getStr("messages");
            if (!StringUtils.hasText(messagesJson)) {
                return Collections.emptyList();
            }
            return ChatMessageDeserializer.messagesFromJson(messagesJson);
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    @Override
    public void updateMessages(Object memoryId, List<ChatMessage> list) {
        String currentMemoryId = memoryId.toString();
        String messagesJson = ChatMessageSerializer.messagesToJson(list == null ? Collections.emptyList() : list);
        JSONObject payload = new JSONObject();
        payload.set("memoryId", currentMemoryId);
        MemoryKeyBuilder.MemoryIdentity memoryIdentity = memoryKeyBuilder.parseMemoryId(currentMemoryId);
        if (memoryIdentity != null) {
            payload.set("userId", memoryIdentity.getUserId());
            payload.set("moduleType", memoryIdentity.getModuleType());
            payload.set("sessionId", memoryIdentity.getSessionId());
        }
        payload.set("updatedAt", LocalDateTime.now().toString());
        payload.set("messages", messagesJson);
        redisTemplate.opsForValue().set(
                memoryKeyBuilder.toRedisKey(currentMemoryId),
                payload.toString(),
                Duration.ofDays(Math.max(memoryTtlDays, 1)));
    }

    @Override
    public void deleteMessages(Object memoryId) {
        redisTemplate.delete(memoryKeyBuilder.toRedisKey(memoryId.toString()));
    }
}
