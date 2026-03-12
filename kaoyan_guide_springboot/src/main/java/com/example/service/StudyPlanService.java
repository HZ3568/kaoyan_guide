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
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

@Service
public class StudyPlanService {
    private static final Logger log = LoggerFactory.getLogger(StudyPlanService.class);

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
     * 生成今日计划
     */
    @Transactional
    public DailyStudyPlan generatePlan(Integer userId, String feedback) {
        LocalDate today = LocalDate.now();

        // 1. 检查今日计划是否已存在
        DailyStudyPlan existingPlan = studyPlanMapper.selectByDate(userId, today);
        if (existingPlan != null) {
            throw new RuntimeException("今日计划已生成，请直接查看");
        }

        // 2. 获取前3天历史记录
        LocalDate startDate = today.minusDays(3);
        LocalDate endDate = today.minusDays(1);
        List<DailyStudyPlan> historyPlans = studyPlanMapper.selectHistory(userId, startDate, endDate);

        // 3. 组装历史上下文
        StringBuilder historyBuilder = new StringBuilder();
        if (historyPlans.isEmpty()) {
            historyBuilder.append("无历史记录，这是第一天学习。");
        } else {
            for (DailyStudyPlan plan : historyPlans) {
                DailyStudyPlan fullPlan = fillPlanTasks(plan, true);
                historyBuilder.append("日期: ").append(plan.getPlanDate()).append("\n");
                historyBuilder.append("任务: ").append(fullPlan.getDailyTasks()).append("\n");
                historyBuilder.append("反馈: ").append(plan.getUserFeedback()).append("\n\n");
            }
        }

        // 4. 调用AI生成规划
        // 简单的清洗feedback，防止注入（虽然AI不太怕注入，但保持整洁）
        String cleanFeedback = feedback == null ? "无" : feedback.trim();
        String finalPrompt = studyPlanAiService.buildPrompt(historyBuilder.toString(), cleanFeedback);
        log.info(
                "study_plan_ai_request userId={} date={} finalPromptPreview={} finalMessagesCount={} whetherUseMemory=false selectedTools=[] retrievalEnabled=false",
                userId,
                today,
                previewText(finalPrompt),
                1);
        String jsonResult = studyPlanAiService.generatePlan(finalPrompt);

        // 5. 清洗和解析JSON
        String cleanJson = cleanJson(jsonResult);
        JSONObject jsonObject;
        try {
            jsonObject = JSONUtil.parseObj(cleanJson);
        } catch (Exception e) {
            log.warn("study_plan_ai_parse_failed userId={} date={} rawPreview={} cleanPreview={}",
                    userId,
                    today,
                    previewText(jsonResult),
                    previewText(cleanJson),
                    e);
            throw new RuntimeException("AI响应格式异常，请稍后重试");
        }

        String advice = jsonObject.getStr("advice");
        TaskNormalizeResult normalizeResult = normalizeTaskList(jsonObject.get("tasks"));
        String tasks = normalizeResult.tasksJson;

        // 6. 落库
        DailyStudyPlan plan = new DailyStudyPlan();
        plan.setUserId(userId);
        plan.setPlanDate(today);
        plan.setUserFeedback(cleanFeedback);
        plan.setAiAdvice(advice);
        LocalDateTime now = LocalDateTime.now();
        plan.setCreateTime(now);
        plan.setUpdateTime(now);

        studyPlanMapper.insert(plan);
        replacePlanTasks(plan.getId(), normalizeResult.tasks);
        plan.setDailyTasks(tasks);

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
        JSONObject task = buildTask(UUID.randomUUID().toString(), normalizedSubject, normalizedContent, false);
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

        for (JSONObject sourceTask : movableTasks) {
            targetTasks.add(buildTask(
                    UUID.randomUUID().toString(),
                    sourceTask.getStr("subject"),
                    sourceTask.getStr("content"),
                    false));
        }

        if (targetPlan == null) {
            DailyStudyPlan newPlan = new DailyStudyPlan();
            newPlan.setUserId(userId);
            newPlan.setPlanDate(targetDate);
            newPlan.setUserFeedback("");
            newPlan.setAiAdvice("由前一日未完成任务自动顺延生成");
            LocalDateTime now = LocalDateTime.now();
            newPlan.setCreateTime(now);
            newPlan.setUpdateTime(now);
            studyPlanMapper.insert(newPlan);
            targetPlan = newPlan;
            replacePlanTasks(targetPlan.getId(), targetTasks);
        } else {
            replacePlanTasks(targetPlan.getId(), targetTasks);
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("sourceDate", sourceDate.toString());
        result.put("targetDate", targetDate.toString());
        result.put("movedCount", movableTasks.size());
        result.put("targetTaskTotal", targetTasks.size());
        return result;
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
            entity.setSortNo(i);
            entity.setCreateTime(now);
            entity.setUpdateTime(now);
            studyPlanMapper.insertTask(entity);
        }
    }

    /**
     * 清洗AI返回的Markdown代码块标记
     */
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
            normalizedTasks.add(buildTask(taskId, subject, content, completed));
        }
        String tasksJson = JSONUtil.toJsonStr(normalizedTasks);
        return new TaskNormalizeResult(normalizedTasks, tasksJson, changed);
    }

    private JSONObject buildTask(String taskId, String subject, String content, boolean completed) {
        JSONObject task = new JSONObject();
        task.set("taskId", taskId);
        task.set("subject", normalizeText(subject));
        task.set("content", normalizeText(content));
        task.set("completed", completed);
        return task;
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

    private String previewText(String text) {
        if (text == null) {
            return "";
        }
        String normalized = text.replace("\r", " ").replace("\n", " ").trim();
        if (normalized.length() <= 300) {
            return normalized;
        }
        return normalized.substring(0, 300) + "...";
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
