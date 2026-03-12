package com.example.repository;

import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.ChatMessageDeserializer;
import dev.langchain4j.data.message.ChatMessageSerializer;
import dev.langchain4j.store.memory.chat.ChatMemoryStore;
import com.example.utils.MemoryKeyBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Repository;
import org.springframework.util.StringUtils;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;

@Repository
public class RedisChatMemoryStore implements ChatMemoryStore {

    @Autowired
    private StringRedisTemplate redisTemplate;

    @Autowired
    private MemoryKeyBuilder memoryKeyBuilder;

    @Override
    public List<ChatMessage> getMessages(Object memoryId) {
        String memoryKey = memoryId.toString();
        String json = redisTemplate.opsForValue().get(memoryKeyBuilder.toRedisKey(memoryKey));
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
        String memoryKey = memoryId.toString();
        String messagesJson = ChatMessageSerializer.messagesToJson(list);
        JSONObject payload = new JSONObject();
        payload.set("memoryKey", memoryKey);
        payload.set("moduleType", memoryKeyBuilder.extractModuleType(memoryKey));
        payload.set("sessionId", memoryKeyBuilder.extractSessionId(memoryKey));
        payload.set("updatedAt", LocalDateTime.now().toString());
        payload.set("messages", messagesJson);
        redisTemplate.opsForValue().set(memoryKeyBuilder.toRedisKey(memoryKey), payload.toString(), Duration.ofDays(1));
    }

    @Override
    public void deleteMessages(Object memoryId) {
        redisTemplate.delete(memoryKeyBuilder.toRedisKey(memoryId));
    }
}
