package com.example.service;

import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.example.entity.DailyStudyPlan;
import com.example.mapper.StudyPlanMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

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
        TaskNormalizeResult normalizeResult = normalizeTaskList(plan.getDailyTasks());
        plan.setDailyTasks(normalizeResult.tasksJson);
        if (normalizeResult.changed) {
            studyPlanMapper.updateDailyTasksByDate(userId, date, normalizeResult.tasksJson);
        }
        return plan;
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
                historyBuilder.append("日期: ").append(plan.getPlanDate()).append("\n");
                historyBuilder.append("任务: ").append(plan.getDailyTasks()).append("\n");
                historyBuilder.append("反馈: ").append(plan.getUserFeedback()).append("\n\n");
            }
        }

        // 4. 调用AI生成规划
        // 简单的清洗feedback，防止注入（虽然AI不太怕注入，但保持整洁）
        String cleanFeedback = feedback == null ? "无" : feedback.trim();
        String jsonResult = studyPlanAiService.generatePlan(historyBuilder.toString(), cleanFeedback);

        // 5. 清洗和解析JSON
        String cleanJson = cleanJson(jsonResult);
        JSONObject jsonObject;
        try {
            jsonObject = JSONUtil.parseObj(cleanJson);
        } catch (Exception e) {
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
        plan.setDailyTasks(tasks);
        plan.setCreateTime(LocalDateTime.now());

        studyPlanMapper.insert(plan);

        return plan;
    }

    public JSONObject addTask(Integer userId, LocalDate date, String subject, String content) {
        String normalizedSubject = normalizeText(subject);
        String normalizedContent = normalizeText(content);
        validateTaskInput(normalizedSubject, normalizedContent);
        DailyStudyPlan plan = studyPlanMapper.selectByDate(userId, date);
        if (plan == null) {
            throw new RuntimeException("当日计划不存在，请先生成计划");
        }
        TaskNormalizeResult normalizeResult = normalizeTaskList(plan.getDailyTasks());
        List<JSONObject> tasks = normalizeResult.tasks;
        JSONObject task = buildTask(UUID.randomUUID().toString(), normalizedSubject, normalizedContent, false);
        tasks.add(task);
        String tasksJson = JSONUtil.toJsonStr(tasks);
        studyPlanMapper.updateDailyTasksByDate(userId, date, tasksJson);
        return task;
    }

    public JSONObject updateTask(Integer userId, LocalDate date, String taskId, String subject, String content) {
        String normalizedSubject = normalizeText(subject);
        String normalizedContent = normalizeText(content);
        validateTaskInput(normalizedSubject, normalizedContent);
        DailyStudyPlan plan = studyPlanMapper.selectByDate(userId, date);
        if (plan == null) {
            throw new RuntimeException("当日计划不存在");
        }
        TaskNormalizeResult normalizeResult = normalizeTaskList(plan.getDailyTasks());
        List<JSONObject> tasks = normalizeResult.tasks;
        JSONObject target = null;
        for (JSONObject task : tasks) {
            if (taskId.equals(task.getStr("taskId"))) {
                task.set("subject", normalizedSubject);
                task.set("content", normalizedContent);
                target = task;
                break;
            }
        }
        if (target == null) {
            throw new RuntimeException("任务不存在");
        }
        String tasksJson = JSONUtil.toJsonStr(tasks);
        studyPlanMapper.updateDailyTasksByDate(userId, date, tasksJson);
        return target;
    }

    public void deleteTask(Integer userId, LocalDate date, String taskId) {
        DailyStudyPlan plan = studyPlanMapper.selectByDate(userId, date);
        if (plan == null) {
            throw new RuntimeException("当日计划不存在");
        }
        TaskNormalizeResult normalizeResult = normalizeTaskList(plan.getDailyTasks());
        List<JSONObject> tasks = normalizeResult.tasks;
        boolean removed = tasks.removeIf(task -> taskId.equals(task.getStr("taskId")));
        if (!removed) {
            throw new RuntimeException("任务不存在");
        }
        studyPlanMapper.updateDailyTasksByDate(userId, date, JSONUtil.toJsonStr(tasks));
    }

    public Map<String, Object> rolloverTasks(Integer userId, LocalDate sourceDate, List<String> onlyTaskIds) {
        DailyStudyPlan sourcePlan = studyPlanMapper.selectByDate(userId, sourceDate);
        if (sourcePlan == null) {
            throw new RuntimeException("当日计划不存在");
        }
        TaskNormalizeResult sourceNormalize = normalizeTaskList(sourcePlan.getDailyTasks());
        List<JSONObject> sourceTasks = sourceNormalize.tasks;
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
        studyPlanMapper.updateDailyTasksByDate(userId, sourceDate, JSONUtil.toJsonStr(sourceTasks));

        LocalDate targetDate = sourceDate.plusDays(1);
        DailyStudyPlan targetPlan = studyPlanMapper.selectByDate(userId, targetDate);
        List<JSONObject> targetTasks;
        if (targetPlan == null) {
            targetTasks = new ArrayList<>();
        } else {
            TaskNormalizeResult targetNormalize = normalizeTaskList(targetPlan.getDailyTasks());
            targetTasks = targetNormalize.tasks;
        }

        for (JSONObject sourceTask : movableTasks) {
            targetTasks.add(buildTask(
                    UUID.randomUUID().toString(),
                    sourceTask.getStr("subject"),
                    sourceTask.getStr("content"),
                    false));
        }

        String targetTasksJson = JSONUtil.toJsonStr(targetTasks);
        if (targetPlan == null) {
            DailyStudyPlan newPlan = new DailyStudyPlan();
            newPlan.setUserId(userId);
            newPlan.setPlanDate(targetDate);
            newPlan.setUserFeedback("");
            newPlan.setAiAdvice("由前一日未完成任务自动顺延生成");
            newPlan.setDailyTasks(targetTasksJson);
            newPlan.setCreateTime(LocalDateTime.now());
            studyPlanMapper.insert(newPlan);
        } else {
            studyPlanMapper.updateDailyTasksByDate(userId, targetDate, targetTasksJson);
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("sourceDate", sourceDate.toString());
        result.put("targetDate", targetDate.toString());
        result.put("movedCount", movableTasks.size());
        result.put("targetTaskTotal", targetTasks.size());
        return result;
    }

    /**
     * 清洗AI返回的Markdown代码块标记
     */
    private String cleanJson(String result) {
        if (result == null)
            return "{}";
        String content = result.trim();
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
            if (isBlank(taskId)) {
                taskId = UUID.randomUUID().toString();
                changed = true;
            }
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
