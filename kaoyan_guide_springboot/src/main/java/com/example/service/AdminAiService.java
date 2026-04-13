package com.example.service;

import com.example.entity.DailyStudyPlan;
import com.example.entity.StudyPlanTask;
import com.example.mapper.StudyPlanMapper;
import com.example.repository.RedisChatMemoryStore;
import com.example.utils.MemoryKeyBuilder;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import dev.langchain4j.data.message.ChatMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class AdminAiService {

    private static final Logger log = LoggerFactory.getLogger(AdminAiService.class);
    private static final String REDIS_CHAT_PREFIX = "chat:memory:";

    private final StringRedisTemplate redisTemplate;
    private final MemoryKeyBuilder memoryKeyBuilder;
    private final RedisChatMemoryStore chatMemoryStore;
    private final StudyPlanMapper studyPlanMapper;

    public AdminAiService(StringRedisTemplate redisTemplate,
                          MemoryKeyBuilder memoryKeyBuilder,
                          RedisChatMemoryStore chatMemoryStore,
                          StudyPlanMapper studyPlanMapper) {
        this.redisTemplate = redisTemplate;
        this.memoryKeyBuilder = memoryKeyBuilder;
        this.chatMemoryStore = chatMemoryStore;
        this.studyPlanMapper = studyPlanMapper;
    }

    // ==================== 咨询会话管理 ====================

    /**
     * 分页获取会话列表（从 Redis keys 扫描）
     */
    public PageInfo<Map<String, Object>> getSessionList(int pageNum, int pageSize,
                                                         Integer userId, String moduleType) {
        // 扫描所有 chat:memory:* keys
        Set<String> keys = redisTemplate.keys(REDIS_CHAT_PREFIX + "*");
        List<Map<String, Object>> sessions = new ArrayList<>();

        if (keys != null) {
            for (String key : keys) {
                String memoryId = key.substring(REDIS_CHAT_PREFIX.length());
                MemoryKeyBuilder.MemoryIdentity identity = memoryKeyBuilder.parseMemoryId(memoryId);
                if (identity == null) continue;

                // 按条件过滤
                if (userId != null && !userId.equals(identity.getUserId())) continue;
                if (moduleType != null && !moduleType.equals(identity.getModuleType())) continue;

                // 读取会话摘要
                String json = redisTemplate.opsForValue().get(key);
                String lastMessage = "";
                LocalDateTime updatedAt = null;
                if (json != null && json.contains("updatedAt")) {
                    try {
                        int updatedAtIdx = json.indexOf("updatedAt");
                        int start = json.indexOf("\"", updatedAtIdx + 11) + 1;
                        int end = json.indexOf("\"", start);
                        if (start > 0 && end > start) {
                            updatedAt = LocalDateTime.parse(json.substring(start, end).replace("T", " ").substring(0, 19));
                        }
                    } catch (Exception ignored) {}
                }

                List<ChatMessage> messages = chatMemoryStore.getMessages(memoryId);
                int messageCount = messages != null ? messages.size() : 0;
                if (messageCount > 0) {
                    ChatMessage last = messages.get(messages.size() - 1);
                    String content = last.toString();
                    lastMessage = content.length() > 80 ? content.substring(0, 80) + "..." : content;
                }

                Map<String, Object> session = new LinkedHashMap<>();
                session.put("memoryKey", memoryId);
                session.put("userId", identity.getUserId());
                session.put("moduleType", identity.getModuleType());
                session.put("sessionId", identity.getSessionId());
                session.put("messageCount", messageCount);
                session.put("lastMessage", lastMessage);
                session.put("updatedAt", updatedAt);
                sessions.add(session);
            }
        }

        // 按 updatedAt 倒序
        sessions.sort((a, b) -> {
            LocalDateTime ta = (LocalDateTime) a.get("updatedAt");
            LocalDateTime tb = (LocalDateTime) b.get("updatedAt");
            if (ta == null && tb == null) return 0;
            if (ta == null) return 1;
            if (tb == null) return -1;
            return tb.compareTo(ta);
        });

        // 手动分页
        int start = (pageNum - 1) * pageSize;
        int end = Math.min(start + pageSize, sessions.size());
        List<Map<String, Object>> pageList = start < sessions.size()
                ? sessions.subList(start, end) : Collections.emptyList();

        PageInfo<Map<String, Object>> page = new PageInfo<>(pageList);
        page.setTotal(sessions.size());
        page.setPages((sessions.size() + pageSize - 1) / pageSize);
        return page;
    }

    /**
     * 获取指定会话的聊天历史
     */
    public List<Map<String, Object>> getSessionHistory(String memoryKey) {
        List<ChatMessage> messages = chatMemoryStore.getMessages(memoryKey);
        return messages.stream().map(msg -> {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("type", msg.type().toString());
            item.put("content", msg.toString());
            return item;
        }).collect(Collectors.toList());
    }

    /**
     * 删除指定会话记录
     */
    public void deleteSession(String memoryKey) {
        chatMemoryStore.deleteMessages(memoryKey);
    }

    // ==================== 学习规划管理 ====================

    /**
     * 分页查询所有用户的学习计划
     */
    public PageInfo<Map<String, Object>> getStudyPlanList(int pageNum, int pageSize, Integer userId) {
        PageHelper.startPage(pageNum, pageSize);
        List<Map<String, Object>> list = studyPlanMapper.selectAllAdminPaged();
        PageInfo<Map<String, Object>> page = new PageInfo<>(list);

        // 按 userId 过滤（如果有）
        if (userId != null && page.getList() != null) {
            List<Map<String, Object>> filtered = page.getList().stream()
                    .filter(m -> userId.equals(m.get("userId")))
                    .collect(Collectors.toList());
            page.setList(filtered);
            page.setTotal(filtered.size());
        }

        // 填充每条计划的任务信息
        if (page.getList() != null) {
            for (Map<String, Object> plan : page.getList()) {
                Long planIdObj = (Long) plan.get("id");
                if (planIdObj != null) {
                    List<StudyPlanTask> tasks = studyPlanMapper.selectTasksByPlanId(planIdObj);
                    plan.put("tasks", tasks);
                    long completed = tasks.stream().filter(t -> Boolean.TRUE.equals(t.getCompleted())).count();
                    plan.put("completedCount", completed);
                    plan.put("totalCount", tasks.size());
                }
            }
        }
        return page;
    }

    /**
     * 管理员修改任务完成状态
     */
    public boolean updateTaskCompleted(Long planId, String taskId, Boolean completed) {
        return studyPlanMapper.updateTaskCompletedAdmin(planId, taskId, completed) > 0;
    }

    /**
     * 管理员删除指定任务
     */
    public boolean deleteTask(Long planId, String taskId) {
        return studyPlanMapper.deleteTaskByPlanIdAndTaskId(planId, taskId) > 0;
    }

    /**
     * 管理员删除整个学习计划
     */
    public void deletePlan(Integer userId, LocalDate date) {
        // 先删任务
        DailyStudyPlan plan = studyPlanMapper.selectByDate(userId, date);
        if (plan != null) {
            studyPlanMapper.deleteTasksByPlanId(plan.getId());
        }
        // 再删计划
        studyPlanMapper.deleteByDateAdmin(userId, date);
    }
}
