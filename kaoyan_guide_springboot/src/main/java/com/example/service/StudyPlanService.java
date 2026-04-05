package com.example.service;

import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.example.entity.DailyStudyPlan;
import com.example.entity.StudyPlanTask;
import com.example.mapper.StudyPlanMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class StudyPlanService {
    private static final Logger log = LoggerFactory.getLogger(StudyPlanService.class);
    private static final String PLAN_STATUS_PENDING = "PENDING";
    private static final String PLAN_STATUS_GENERATED = "GENERATED";
    private static final String TASK_SOURCE_DEFERRED = "DEFERRED";
    private static final String TASK_SOURCE_GENERATED = "GENERATED";

    @Autowired
    private StudyPlanMapper studyPlanMapper;

    @Autowired
    private StudyPlanAiService studyPlanAiService;

    /**
     * 获取指定日期的计划
     */
    public DailyStudyPlan getPlanByDate(Integer userId, LocalDate date) {
        DailyStudyPlan plan = studyPlanMapper.selectByDate(userId, date);
        if (plan == null) {
            return null;
        }
        return fillPlanTasks(plan, true);
    }

    /**
     * 删除指定日期的计划
     */
    public void deletePlan(Integer userId, LocalDate date) {
        studyPlanMapper.deleteByDate(userId, date);
    }

    /**
     * 生成今日计划（同步，已不推荐直接调用，建议通过异步接口）。
     * 保留供兼容和测试使用。
     */
    public DailyStudyPlan generatePlan(Integer userId, String feedback) {
        LocalDate today = LocalDate.now();
        DailyStudyPlan plan = studyPlanMapper.selectByDate(userId, today);
        if (plan != null && PLAN_STATUS_GENERATED.equalsIgnoreCase(plan.getPlanStatus())) {
            throw new RuntimeException("今日计划已生成，请直接查看");
        }

        // 构造 prompt 并调用 AI（包含耗时日志）
        String prompt = buildGeneratePrompt(userId, today, feedback);
        log.info("[StudyPlan] AI 调用开始 userId={} date={} promptLen={}", userId, today, prompt.length());
        long aiStart = System.currentTimeMillis();
        String jsonResult = studyPlanAiService.generatePlan(prompt);
        log.info("[StudyPlan] AI 调用完成 userId={} cost={}ms", userId, System.currentTimeMillis() - aiStart);

        // 解析并落库
        return parseAndSavePlan(userId, today, feedback, jsonResult, plan);
    }

    /**
     * 核心生成逻辑（供异步消费者调用）：构造 prompt → 调 AI → 解析 → 落库。
     * 所有关键步骤都打印耗时日志。
     */
    public DailyStudyPlan generatePlanInternal(Integer userId, String feedback) {
        LocalDate today = LocalDate.now();
        long t0 = System.currentTimeMillis();

        DailyStudyPlan existingPlan = studyPlanMapper.selectByDate(userId, today);
        if (existingPlan != null && PLAN_STATUS_GENERATED.equalsIgnoreCase(existingPlan.getPlanStatus())) {
            throw new RuntimeException("今日计划已生成，请直接查看");
        }

        // 1. 构造 prompt（含历史摘要查询）
        long promptStart = System.currentTimeMillis();
        String prompt = buildGeneratePrompt(userId, today, feedback);
        log.info("[StudyPlan] prompt 构造完成 userId={} promptLen={} cost={}ms",
                userId, prompt.length(), System.currentTimeMillis() - promptStart);

        // 2. 调用大模型
        long aiStart = System.currentTimeMillis();
        log.info("[StudyPlan] AI 调用开始 userId={} date={}", userId, today);
        String jsonResult = studyPlanAiService.generatePlan(prompt);
        log.info("[StudyPlan] AI 调用完成 userId={} aiCost={}ms responseLen={}",
                userId, System.currentTimeMillis() - aiStart,
                jsonResult == null ? 0 : jsonResult.length());

        // 3. 解析 & 落库
        long saveStart = System.currentTimeMillis();
        DailyStudyPlan saved = parseAndSavePlan(userId, today, feedback, jsonResult, existingPlan);
        log.info("[StudyPlan] 解析落库完成 userId={} saveCost={}ms totalCost={}ms",
                userId, System.currentTimeMillis() - saveStart, System.currentTimeMillis() - t0);

        return saved;
    }

    /**
     * 构造生成 prompt：批量查询历史计划和任务，组装为精简摘要。
     * 避免 N+1：一次查出所有历史计划，再一次性批量查出对应任务，在内存分组。
     */
    private String buildGeneratePrompt(Integer userId, LocalDate today, String feedback) {
        long queryStart = System.currentTimeMillis();

        LocalDate startDate = today.minusDays(3);
        LocalDate endDate = today.minusDays(1);
        List<DailyStudyPlan> historyPlans = studyPlanMapper.selectHistory(userId, startDate, endDate);

        String historySummary;
        if (historyPlans.isEmpty()) {
            historySummary = "无历史记录，这是第一天学习。";
        } else {
            // 批量查出这些计划对应的所有任务，在内存中按 planId 分组
            List<Long> planIds = historyPlans.stream()
                    .map(DailyStudyPlan::getId)
                    .collect(Collectors.toList());
            List<StudyPlanTask> allTasks = studyPlanMapper.selectTasksByPlanIds(planIds);
            Map<Long, List<StudyPlanTask>> tasksByPlanId = allTasks.stream()
                    .collect(Collectors.groupingBy(StudyPlanTask::getPlanId));

            log.info("[StudyPlan] 历史查询完成 userId={} planCount={} taskCount={} cost={}ms",
                    userId, historyPlans.size(), allTasks.size(), System.currentTimeMillis() - queryStart);

            historySummary = buildHistorySummary(historyPlans, tasksByPlanId);
        }

        String cleanFeedback = feedback == null ? "无" : feedback.trim();
        return studyPlanAiService.buildPrompt(historySummary, cleanFeedback);
    }

    /**
     * 将历史计划列表组装为精简摘要文本，避免将完整 JSON 拼入 prompt。
     * 只提炼：日期、各科完成/未完成情况、是否有连续未完成、用户反馈摘要。
     */
    private String buildHistorySummary(List<DailyStudyPlan> plans,
                                        Map<Long, List<StudyPlanTask>> tasksByPlanId) {
        StringBuilder sb = new StringBuilder();
        for (DailyStudyPlan plan : plans) {
            List<StudyPlanTask> tasks = tasksByPlanId.getOrDefault(plan.getId(), Collections.emptyList());
            long total = tasks.size();
            long done = tasks.stream().filter(t -> Boolean.TRUE.equals(t.getCompleted())).count();
            long undone = total - done;

            // 统计各科未完成情况
            Map<String, Long> undoneBySubject = tasks.stream()
                    .filter(t -> !Boolean.TRUE.equals(t.getCompleted()))
                    .collect(Collectors.groupingBy(
                            t -> t.getSubject() == null ? "未知" : t.getSubject(),
                            Collectors.counting()));

            sb.append("日期: ").append(plan.getPlanDate()).append("\n");
            sb.append("完成情况: 共").append(total).append("项，完成").append(done).append("项，未完成").append(undone).append("项\n");
            if (!undoneBySubject.isEmpty()) {
                sb.append("未完成科目: ");
                undoneBySubject.forEach((subject, count) ->
                        sb.append(subject).append("(").append(count).append("项) "));
                sb.append("\n");
            }
            String feedbackText = plan.getUserFeedback();
            if (feedbackText != null && !feedbackText.trim().isEmpty()) {
                String trimmed = feedbackText.trim();
                // 截断过长反馈，避免撑大 prompt
                sb.append("学生反馈: ").append(trimmed.length() > 80 ? trimmed.substring(0, 80) + "…" : trimmed).append("\n");
            }
            sb.append("\n");
        }
        return sb.toString();
    }

    /**
     * 解析 AI 响应 JSON 并落库
     */
    private DailyStudyPlan parseAndSavePlan(Integer userId, LocalDate today, String feedback,
                                             String jsonResult, DailyStudyPlan existingPlan) {
        String cleanJson = cleanJson(jsonResult);
        JSONObject jsonObject;
        try {
            jsonObject = JSONUtil.parseObj(cleanJson);
        } catch (Exception e) {
            log.warn("[StudyPlan] AI 响应解析失败 userId={} rawLen={} cleanLen={}",
                    userId, jsonResult == null ? 0 : jsonResult.length(), cleanJson.length(), e);
            throw new RuntimeException("AI响应格式异常，请稍后重试");
        }

        String advice = jsonObject.getStr("advice");
        TaskNormalizeResult normalizeResult = normalizeTaskList(jsonObject.get("tasks"));
        List<JSONObject> generatedTasks = new ArrayList<>();
        for (JSONObject task : normalizeResult.tasks) {
            String subject = task.getStr("subject");
            String content = task.getStr("content");
            if (isBlank(content)) {
                log.warn("[StudyPlan] AI 任务 content 为空，跳过 subject={}", subject);
                continue;
            }
            generatedTasks.add(buildTask(
                    UUID.randomUUID().toString(),
                    subject,
                    content,
                    false,
                    TASK_SOURCE_GENERATED));
        }
        if (generatedTasks.isEmpty()) {
            throw new RuntimeException("AI未返回有效任务，请重试");
        }

        String cleanFeedback = feedback == null ? "无" : feedback.trim();
        return savePlanWithTasks(userId, today, cleanFeedback, advice, generatedTasks, existingPlan);
    }

    /**
     * 事务方法：仅包裹数据库写入操作
     */
    @Transactional
    public DailyStudyPlan savePlanWithTasks(Integer userId, LocalDate today, String cleanFeedback,
                                              String advice, List<JSONObject> generatedTasks,
                                              DailyStudyPlan existingPlan) {
        LocalDateTime now = LocalDateTime.now();
        DailyStudyPlan plan = existingPlan;
        if (plan == null) {
            plan = new DailyStudyPlan();
            plan.setUserId(userId);
            plan.setPlanDate(today);
            plan.setUserFeedback(cleanFeedback);
            plan.setAiAdvice(advice);
            plan.setPlanStatus(PLAN_STATUS_PENDING);
            plan.setCreateTime(now);
            plan.setUpdateTime(now);
            studyPlanMapper.insert(plan);
        }

        TaskNormalizeResult existingNormalize = normalizeTaskEntities(
                studyPlanMapper.selectTasksByPlanId(plan.getId()));
        List<JSONObject> mergedTasks = new ArrayList<>(existingNormalize.tasks);
        Set<String> existingSignatures = new HashSet<>();
        for (JSONObject task : mergedTasks) {
            existingSignatures.add(taskSignature(task));
        }
        for (JSONObject task : generatedTasks) {
            String signature = taskSignature(task);
            if (!existingSignatures.contains(signature)) {
                mergedTasks.add(task);
                existingSignatures.add(signature);
            }
        }
        replacePlanTasks(plan.getId(), mergedTasks);
        plan.setDailyTasks(JSONUtil.toJsonStr(mergedTasks));
        plan.setUserFeedback(cleanFeedback);
        plan.setAiAdvice(advice);
        plan.setPlanStatus(PLAN_STATUS_GENERATED);
        plan.setUpdateTime(now);
        studyPlanMapper.updatePlanCoreById(plan);

        return plan;
    }

    @Transactional
    public JSONObject addTask(Integer userId, LocalDate date, String subject, String content) {
        String normalizedSubject = normalizeText(subject);
        String normalizedContent = normalizeText(content);
        validateTaskInput(normalizedSubject, normalizedContent);
        DailyStudyPlan plan = studyPlanMapper.selectByDate(userId, date);
        if (plan == null) {
            throw new RuntimeException("当日计划不存在，请先生成计划");
        }
        TaskNormalizeResult normalizeResult = normalizeTaskEntities(studyPlanMapper.selectTasksByPlanId(plan.getId()));
        List<JSONObject> tasks = new ArrayList<>(normalizeResult.tasks);
        JSONObject task = buildTask(
                UUID.randomUUID().toString(),
                normalizedSubject,
                normalizedContent,
                false,
                TASK_SOURCE_GENERATED);
        tasks.add(task);
        replacePlanTasks(plan.getId(), tasks);
        return task;
    }

    @Transactional
    public JSONObject updateTask(Integer userId, LocalDate date, String taskId, String subject, String content) {
        String normalizedSubject = normalizeText(subject);
        String normalizedContent = normalizeText(content);
        validateTaskInput(normalizedSubject, normalizedContent);
        DailyStudyPlan plan = studyPlanMapper.selectByDate(userId, date);
        if (plan == null) {
            throw new RuntimeException("当日计划不存在");
        }
        String normalizedTaskId = normalizeText(taskId);
        if (isBlank(normalizedTaskId)) {
            throw new RuntimeException("任务不存在");
        }
        int affected = studyPlanMapper.updateTaskByPlanIdAndTaskId(plan.getId(), normalizedTaskId, normalizedSubject,
                normalizedContent);
        if (affected <= 0) {
            throw new RuntimeException("任务不存在");
        }
        TaskNormalizeResult normalizeResult = normalizeTaskEntities(studyPlanMapper.selectTasksByPlanId(plan.getId()));
        if (normalizeResult.changed) {
            replacePlanTasks(plan.getId(), normalizeResult.tasks);
        }
        for (JSONObject task : normalizeResult.tasks) {
            if (normalizedTaskId.equals(task.getStr("taskId"))) {
                return task;
            }
        }
        throw new RuntimeException("任务不存在");
    }

    @Transactional
    public JSONObject updateTaskCompleted(Integer userId, LocalDate date, String taskId, boolean completed) {
        DailyStudyPlan plan = studyPlanMapper.selectByDate(userId, date);
        if (plan == null) {
            throw new RuntimeException("当日计划不存在");
        }
        String normalizedTaskId = normalizeText(taskId);
        if (isBlank(normalizedTaskId)) {
            throw new RuntimeException("任务不存在");
        }
        int affected = studyPlanMapper.updateTaskCompletedByPlanIdAndTaskId(plan.getId(), normalizedTaskId, completed);
        if (affected <= 0) {
            throw new RuntimeException("任务不存在");
        }
        TaskNormalizeResult normalizeResult = normalizeTaskEntities(studyPlanMapper.selectTasksByPlanId(plan.getId()));
        if (normalizeResult.changed) {
            replacePlanTasks(plan.getId(), normalizeResult.tasks);
        }
        for (JSONObject task : normalizeResult.tasks) {
            if (normalizedTaskId.equals(task.getStr("taskId"))) {
                return task;
            }
        }
        throw new RuntimeException("任务不存在");
    }

    @Transactional
    public void deleteTask(Integer userId, LocalDate date, String taskId) {
        DailyStudyPlan plan = studyPlanMapper.selectByDate(userId, date);
        if (plan == null) {
            throw new RuntimeException("当日计划不存在");
        }
        String normalizedTaskId = normalizeText(taskId);
        if (isBlank(normalizedTaskId)) {
            throw new RuntimeException("任务不存在");
        }
        int affected = studyPlanMapper.deleteTaskByPlanIdAndTaskId(plan.getId(), normalizedTaskId);
        if (affected <= 0) {
            throw new RuntimeException("任务不存在");
        }
    }

    @Transactional
    public Map<String, Object> rolloverTasks(Integer userId, LocalDate sourceDate, List<String> onlyTaskIds) {
        DailyStudyPlan sourcePlan = studyPlanMapper.selectByDate(userId, sourceDate);
        if (sourcePlan == null) {
            throw new RuntimeException("当日计划不存在");
        }
        TaskNormalizeResult sourceNormalize = normalizeTaskEntities(
                studyPlanMapper.selectTasksByPlanId(sourcePlan.getId()));
        List<JSONObject> sourceTasks = new ArrayList<>(sourceNormalize.tasks);
        Set<String> requiredTaskIds = new HashSet<>();
        if (onlyTaskIds != null) {
            for (String taskId : onlyTaskIds) {
                String normalizedId = normalizeText(taskId);
                if (!isBlank(normalizedId)) {
                    requiredTaskIds.add(normalizedId);
                }
            }
        }

        List<JSONObject> movableTasks = new ArrayList<>();
        for (JSONObject task : sourceTasks) {
            String currentTaskId = task.getStr("taskId");
            boolean completed = Boolean.TRUE.equals(task.getBool("completed"));
            if (completed) {
                continue;
            }
            if (requiredTaskIds.isEmpty() || requiredTaskIds.contains(currentTaskId)) {
                movableTasks.add(task);
            }
        }

        if (!requiredTaskIds.isEmpty()) {
            for (String taskId : requiredTaskIds) {
                boolean matched = false;
                for (JSONObject task : movableTasks) {
                    if (taskId.equals(task.getStr("taskId"))) {
                        matched = true;
                        break;
                    }
                }
                if (!matched) {
                    throw new RuntimeException("指定任务不存在或已完成");
                }
            }
        }

        if (movableTasks.isEmpty()) {
            throw new RuntimeException("没有可顺延的未完成任务");
        }

        Set<String> movingTaskIds = new HashSet<>();
        for (JSONObject task : movableTasks) {
            movingTaskIds.add(task.getStr("taskId"));
        }
        sourceTasks.removeIf(task -> movingTaskIds.contains(task.getStr("taskId")));
        replacePlanTasks(sourcePlan.getId(), sourceTasks);

        LocalDate targetDate = sourceDate.plusDays(1);
        DailyStudyPlan targetPlan = studyPlanMapper.selectByDate(userId, targetDate);
        List<JSONObject> targetTasks;
        if (targetPlan == null) {
            targetTasks = new ArrayList<>();
        } else {
            TaskNormalizeResult targetNormalize = normalizeTaskEntities(
                    studyPlanMapper.selectTasksByPlanId(targetPlan.getId()));
            targetTasks = new ArrayList<>(targetNormalize.tasks);
        }

        Set<String> targetSignatures = new HashSet<>();
        for (JSONObject targetTask : targetTasks) {
            targetSignatures.add(taskSignature(targetTask));
        }
        int movedCount = 0;
        for (JSONObject sourceTask : movableTasks) {
            JSONObject deferredTask = buildTask(
                    UUID.randomUUID().toString(),
                    sourceTask.getStr("subject"),
                    sourceTask.getStr("content"),
                    false,
                    TASK_SOURCE_DEFERRED);
            String signature = taskSignature(deferredTask);
            if (!targetSignatures.contains(signature)) {
                targetTasks.add(deferredTask);
                targetSignatures.add(signature);
                movedCount++;
            }
        }

        if (targetPlan == null) {
            DailyStudyPlan newPlan = new DailyStudyPlan();
            newPlan.setUserId(userId);
            newPlan.setPlanDate(targetDate);
            newPlan.setUserFeedback("");
            newPlan.setAiAdvice("由前一日未完成任务自动顺延生成");
            newPlan.setPlanStatus(PLAN_STATUS_PENDING);
            LocalDateTime now = LocalDateTime.now();
            newPlan.setCreateTime(now);
            newPlan.setUpdateTime(now);
            studyPlanMapper.insert(newPlan);
            targetPlan = newPlan;
            replacePlanTasks(targetPlan.getId(), targetTasks);
        } else {
            if (isBlank(targetPlan.getPlanStatus())) {
                studyPlanMapper.updatePlanStatusById(targetPlan.getId(), PLAN_STATUS_PENDING, LocalDateTime.now());
            }
            replacePlanTasks(targetPlan.getId(), targetTasks);
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("sourceDate", sourceDate.toString());
        result.put("targetDate", targetDate.toString());
        result.put("movedCount", movedCount);
        result.put("targetTaskTotal", targetTasks.size());
        return result;
    }

    public Map<String, Object> buildPlanResponse(DailyStudyPlan plan) {
        if (plan == null) {
            return null;
        }
        TaskNormalizeResult normalizeResult = normalizeTaskEntities(studyPlanMapper.selectTasksByPlanId(plan.getId()));
        if (normalizeResult.changed) {
            replacePlanTasks(plan.getId(), normalizeResult.tasks);
        }
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("planId", plan.getId());
        response.put("planDate", plan.getPlanDate());
        response.put("planStatus", isBlank(plan.getPlanStatus()) ? PLAN_STATUS_PENDING : plan.getPlanStatus());
        response.put("userFeedback", plan.getUserFeedback());
        response.put("aiAdvice", plan.getAiAdvice());
        response.put("taskList", normalizeResult.tasks);
        response.put("dailyTasks", normalizeResult.tasksJson);
        return response;
    }

    private DailyStudyPlan fillPlanTasks(DailyStudyPlan plan, boolean normalizeAndPersist) {
        TaskNormalizeResult normalizeResult = normalizeTaskEntities(studyPlanMapper.selectTasksByPlanId(plan.getId()));
        plan.setDailyTasks(normalizeResult.tasksJson);
        if (normalizeAndPersist && normalizeResult.changed) {
            replacePlanTasks(plan.getId(), normalizeResult.tasks);
        }
        return plan;
    }

    private void replacePlanTasks(Long planId, List<JSONObject> tasks) {
        studyPlanMapper.deleteTasksByPlanId(planId);
        if (tasks == null || tasks.isEmpty()) {
            return;
        }
        LocalDateTime now = LocalDateTime.now();
        for (int i = 0; i < tasks.size(); i++) {
            JSONObject task = tasks.get(i);
            StudyPlanTask entity = new StudyPlanTask();
            entity.setTaskId(task.getStr("taskId"));
            entity.setPlanId(planId);
            entity.setSubject(task.getStr("subject"));
            entity.setContent(task.getStr("content"));
            entity.setCompleted(Boolean.TRUE.equals(task.getBool("completed")));
            entity.setTaskSource(resolveTaskSource(task.getStr("taskSource")));
            entity.setSortNo(i);
            entity.setCreateTime(now);
            entity.setUpdateTime(now);
            studyPlanMapper.insertTask(entity);
        }
    }

    private String cleanJson(String result) {
        if (result == null) {
            return "{}";
        }
        String content = stripCodeFence(result.trim());
        int firstBrace = content.indexOf("{");
        int lastBrace = content.lastIndexOf("}");
        if (firstBrace >= 0 && lastBrace > firstBrace) {
            return content.substring(firstBrace, lastBrace + 1).trim();
        }
        return content.trim();
    }

    private String stripCodeFence(String content) {
        if (content.startsWith("```json")) {
            content = content.substring(7);
        } else if (content.startsWith("```")) {
            content = content.substring(3);
        }
        if (content.endsWith("```")) {
            content = content.substring(0, content.length() - 3);
        }
        return content.trim();
    }

    private void validateTaskInput(String subject, String content) {
        if (isBlank(subject) || isBlank(content) || subject.length() > 20 || content.length() > 200) {
            throw new RuntimeException("参数不合法");
        }
    }

    private TaskNormalizeResult normalizeTaskEntities(List<StudyPlanTask> taskEntities) {
        JSONArray sourceArray = new JSONArray();
        if (taskEntities != null) {
            for (StudyPlanTask taskEntity : taskEntities) {
                JSONObject source = new JSONObject();
                source.set("taskId", taskEntity.getTaskId());
                source.set("subject", taskEntity.getSubject());
                source.set("content", taskEntity.getContent());
                source.set("completed", Boolean.TRUE.equals(taskEntity.getCompleted()));
                source.set("taskSource", resolveTaskSource(taskEntity.getTaskSource()));
                sourceArray.add(source);
            }
        }
        return normalizeTaskList(sourceArray);
    }

    private TaskNormalizeResult normalizeTaskList(Object tasksRaw) {
        JSONArray sourceArray;
        try {
            if (tasksRaw == null || isBlank(String.valueOf(tasksRaw)) || "null".equals(String.valueOf(tasksRaw))) {
                sourceArray = new JSONArray();
            } else if (tasksRaw instanceof JSONArray) {
                sourceArray = (JSONArray) tasksRaw;
            } else {
                sourceArray = JSONUtil.parseArray(tasksRaw);
            }
        } catch (Exception e) {
            sourceArray = new JSONArray();
        }

        List<JSONObject> normalizedTasks = new ArrayList<>();
        Set<String> usedTaskIds = new HashSet<>();
        boolean changed = false;
        for (Object item : sourceArray) {
            JSONObject sourceTask;
            try {
                sourceTask = JSONUtil.parseObj(item);
            } catch (Exception e) {
                changed = true;
                continue;
            }
            String taskId = normalizeText(sourceTask.getStr("taskId"));
            if (isBlank(taskId) || usedTaskIds.contains(taskId)) {
                taskId = UUID.randomUUID().toString();
                changed = true;
            }
            usedTaskIds.add(taskId);
            String subject = normalizeText(sourceTask.getStr("subject"));
            if (subject.length() > 20) {
                subject = subject.substring(0, 20);
                changed = true;
            }
            String content = normalizeText(sourceTask.getStr("content"));
            if (content.length() > 200) {
                content = content.substring(0, 200);
                changed = true;
            }
            Boolean completedRaw = sourceTask.getBool("completed");
            boolean completed = completedRaw != null && completedRaw;
            String taskSource = resolveTaskSource(sourceTask.getStr("taskSource"));
            if (completedRaw == null) {
                changed = true;
            }
            if (!taskId.equals(sourceTask.getStr("taskId"))) {
                changed = true;
            }
            if (!subject.equals(normalizeText(sourceTask.getStr("subject")))) {
                changed = true;
            }
            if (!content.equals(normalizeText(sourceTask.getStr("content")))) {
                changed = true;
            }
            if (!taskSource.equals(resolveTaskSource(sourceTask.getStr("taskSource")))) {
                changed = true;
            }
            normalizedTasks.add(buildTask(taskId, subject, content, completed, taskSource));
        }
        String tasksJson = JSONUtil.toJsonStr(normalizedTasks);
        return new TaskNormalizeResult(normalizedTasks, tasksJson, changed);
    }

    private JSONObject buildTask(String taskId, String subject, String content, boolean completed, String taskSource) {
        JSONObject task = new JSONObject();
        task.set("taskId", taskId);
        task.set("subject", normalizeText(subject));
        task.set("content", normalizeText(content));
        task.set("completed", completed);
        task.set("taskSource", resolveTaskSource(taskSource));
        return task;
    }

    private String resolveTaskSource(String taskSource) {
        String normalizedSource = normalizeText(taskSource).toUpperCase();
        if (TASK_SOURCE_DEFERRED.equals(normalizedSource)) {
            return TASK_SOURCE_DEFERRED;
        }
        return TASK_SOURCE_GENERATED;
    }

    private String taskSignature(JSONObject task) {
        return normalizeText(task.getStr("subject")) + "||" + normalizeText(task.getStr("content"));
    }

    private String normalizeText(String text) {
        if (text == null) {
            return "";
        }
        return text.trim();
    }

    private boolean isBlank(String text) {
        return text == null || text.trim().isEmpty();
    }

    private static class TaskNormalizeResult {
        private final List<JSONObject> tasks;
        private final String tasksJson;
        private final boolean changed;

        private TaskNormalizeResult(List<JSONObject> tasks, String tasksJson, boolean changed) {
            this.tasks = tasks;
            this.tasksJson = tasksJson;
            this.changed = changed;
        }
    }
}
