package com.example.service;

import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.example.entity.DailyStudyPlan;
import com.example.entity.StudyPlanTask;
import com.example.entity.User;
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
import java.time.format.DateTimeFormatter;
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
    private final UserService userService;

    public AdminAiService(StringRedisTemplate redisTemplate,
                          MemoryKeyBuilder memoryKeyBuilder,
                          RedisChatMemoryStore chatMemoryStore,
                          StudyPlanMapper studyPlanMapper,
                          UserService userService) {
        this.redisTemplate = redisTemplate;
        this.memoryKeyBuilder = memoryKeyBuilder;
        this.chatMemoryStore = chatMemoryStore;
        this.studyPlanMapper = studyPlanMapper;
        this.userService = userService;
    }

    // ==================== 咨询会话管理 ====================

    public PageInfo<Map<String, Object>> getSessionList(int pageNum, int pageSize,
                                                         Integer userId, String moduleType) {
        Set<String> keys = redisTemplate.keys(REDIS_CHAT_PREFIX + "*");
        List<Map<String, Object>> sessions = new ArrayList<>();

        if (keys != null) {
            for (String key : keys) {
                String memoryId = key.substring(REDIS_CHAT_PREFIX.length());
                MemoryKeyBuilder.MemoryIdentity identity = memoryKeyBuilder.parseMemoryId(memoryId);
                if (identity == null) continue;

                if (userId != null && !userId.equals(identity.getUserId())) continue;
                if (moduleType != null && !moduleType.equals(identity.getModuleType())) continue;

                String json = redisTemplate.opsForValue().get(key);
                LocalDateTime lastActiveTime = null;
                int messageCount = 0;

                if (json != null && json.startsWith("{")) {
                    try {
                        JSONObject obj = JSONUtil.parseObj(json);
                        String updatedAtStr = obj.getStr("updatedAt");
                        if (updatedAtStr != null && !updatedAtStr.isBlank()) {
                            lastActiveTime = LocalDateTime.parse(updatedAtStr, DateTimeFormatter.ISO_LOCAL_DATE_TIME);
                        }
                    } catch (Exception e) {
                        log.warn("解析会话更新时间失败: key={}", key, e);
                    }
                }

                List<ChatMessage> messages = chatMemoryStore.getMessages(memoryId);
                messageCount = messages != null ? messages.size() : 0;

                String userName = null;
                try {
                    User user = userService.selectById(identity.getUserId());
                    if (user != null) userName = user.getName();
                } catch (Exception e) {
                    log.warn("查找用户名失败: userId={}", identity.getUserId());
                }

                Map<String, Object> session = new LinkedHashMap<>();
                session.put("memoryKey", memoryId);
                session.put("userId", identity.getUserId());
                session.put("userName", userName != null ? userName : "用户" + identity.getUserId());
                session.put("moduleType", identity.getModuleType());
                session.put("messageCount", messageCount);
                session.put("lastActiveTime", lastActiveTime);
                sessions.add(session);
            }
        }

        sessions.sort((a, b) -> {
            LocalDateTime ta = (LocalDateTime) a.get("lastActiveTime");
            LocalDateTime tb = (LocalDateTime) b.get("lastActiveTime");
            if (ta == null && tb == null) return 0;
            if (ta == null) return 1;
            if (tb == null) return -1;
            return tb.compareTo(ta);
        });

        int total = sessions.size();
        int start = (pageNum - 1) * pageSize;
        int end = Math.min(start + pageSize, total);
        List<Map<String, Object>> pageList = start < total
                ? sessions.subList(start, end) : Collections.emptyList();

        PageInfo<Map<String, Object>> page = new PageInfo<>(pageList);
        page.setTotal(total);
        page.setPages((total + pageSize - 1) / pageSize);
        return page;
    }

    public List<Map<String, Object>> getSessionHistory(String memoryKey) {
        List<ChatMessage> messages = chatMemoryStore.getMessages(memoryKey);
        return messages.stream().map(msg -> {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("type", msg.type().toString());
            item.put("content", msg.toString());
            return item;
        }).collect(Collectors.toList());
    }

    public void deleteSession(String memoryKey) {
        chatMemoryStore.deleteMessages(memoryKey);
    }

    // ==================== 学习规划管理 ====================

    public PageInfo<Map<String, Object>> getStudyPlanList(int pageNum, int pageSize, Integer userId) {
        long t0 = System.currentTimeMillis();
        PageHelper.startPage(pageNum, pageSize);
        List<Map<String, Object>> list = studyPlanMapper.selectAllAdminPaged();
        long t1 = System.currentTimeMillis();
        PageInfo<Map<String, Object>> page = new PageInfo<>(list);

        if (userId != null && page.getList() != null) {
            List<Map<String, Object>> filtered = page.getList().stream()
                    .filter(m -> userId.equals(m.get("userId")))
                    .collect(Collectors.toList());
            page.setList(filtered);
            page.setTotal(filtered.size());
        }

        if (page.getList() != null) {
            for (Map<String, Object> plan : page.getList()) {
                Object idVal = plan.get("planId");
                Long planId = null;
                if (idVal instanceof Number) planId = ((Number) idVal).longValue();
                if (planId == null) {
                    log.warn("[AdminAi] 计划缺少 planId，跳过 task 聚合 plan={}", plan);
                    continue;
                }

                List<StudyPlanTask> tasks = studyPlanMapper.selectTasksByPlanId(planId);
                plan.put("tasks", tasks);

                int total = tasks.size();
                int completed = (int) tasks.stream().filter(t -> t.getCompleted() != null && t.getCompleted()).count();
                int percent = total > 0 ? Math.round((float) completed / total * 100) : 0;

                plan.put("totalCount", total);
                plan.put("completedCount", completed);
                plan.put("taskPercent", percent);
                plan.put("planStatus", computePlanStatus(total, completed));
                plan.put("userFeedbackSummary", truncate(String.valueOf(plan.get("userFeedback")), 15));
                plan.put("aiAdviceSummary", truncate(String.valueOf(plan.get("aiAdvice")), 15));
            }
        }
        long t2 = System.currentTimeMillis();
        log.info("[AdminAi] 查询学习计划列表 userId={} pageNum={} pageSize={} 查库cost={}ms 聚合cost={}ms 总cost={}ms",
                userId, pageNum, pageSize, t1 - t0, t2 - t1, t2 - t0);
        return page;
    }

    private String truncate(String text, int maxLen) {
        if (text == null || "null".equals(text)) return "";
        String s = text.trim();
        if (s.length() <= maxLen) return s;
        return s.substring(0, maxLen) + "...";
    }

    public Map<String, Object> getStudyPlanDetail(Long planId) {
        if (planId == null) return null;
        Map<String, Object> plan = studyPlanMapper.selectAdminDetailById(planId);
        if (plan == null) return null;

        List<StudyPlanTask> tasks = studyPlanMapper.selectTasksByPlanId(planId);
        plan.put("tasks", tasks);

        int total = tasks.size();
        int completed = (int) tasks.stream().filter(t -> t.getCompleted() != null && t.getCompleted()).count();
        int percent = total > 0 ? Math.round((float) completed / total * 100) : 0;

        plan.put("totalCount", total);
        plan.put("completedCount", completed);
        plan.put("taskPercent", percent);
        plan.put("planStatus", computePlanStatus(total, completed));

        return plan;
    }

    private String computePlanStatus(int total, int completed) {
        if (total == 0) return "PENDING";
        if (completed == 0) return "PENDING";
        if (completed >= total) return "GENERATED";
        return "IN_PROGRESS";
    }

    public boolean updateTaskCompleted(Long planId, String taskId, Boolean completed) {
        boolean updated = studyPlanMapper.updateTaskCompletedAdmin(planId, taskId, completed) > 0;
        if (updated) syncPlanStats(planId);
        return updated;
    }

    public boolean deleteTask(Long planId, String taskId) {
        boolean deleted = studyPlanMapper.deleteTaskByPlanIdAndTaskId(planId, taskId) > 0;
        if (deleted) syncPlanStats(planId);
        return deleted;
    }

    private void syncPlanStats(Long planId) {
        if (planId == null) return;
        try {
            List<StudyPlanTask> tasks = studyPlanMapper.selectTasksByPlanId(planId);
            int total = tasks.size();
            int completed = (int) tasks.stream().filter(t -> t.getCompleted() != null && t.getCompleted()).count();
            String status = computePlanStatus(total, completed);
            studyPlanMapper.updatePlanStatusById(planId, status, LocalDateTime.now());
        } catch (Exception e) {
            log.error("同步计划统计失败: planId={}", planId, e);
        }
    }

    /**
     * 管理员删除整个学习计划（同时清理子任务和主表记录）
     */
    public void deletePlan(Integer userId, LocalDate date) {
        DailyStudyPlan plan = studyPlanMapper.selectByDate(userId, date);
        if (plan != null) {
            studyPlanMapper.deleteTasksByPlanId(plan.getId());
        }
        studyPlanMapper.deleteByDateAdmin(userId, date);
        log.info("[AdminAi] 删除计划 userId={} date={} planId={}", userId, date, plan != null ? plan.getId() : null);
    }
}
