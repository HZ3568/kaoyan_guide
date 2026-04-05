package com.example.controller;

import com.example.common.Result;
import com.example.entity.Account;
import com.example.entity.DailyStudyPlan;
import com.example.entity.StudyPlanGenerateMessage;
import com.example.entity.StudyPlanGenerateTask;
import com.example.entity.User;
import com.example.exception.CustomException;
import com.example.mapper.StudyPlanGenerateTaskMapper;
import com.example.service.StudyPlanProducer;
import com.example.service.StudyPlanService;
import com.example.utils.TokenUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeParseException;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/study-plan")
public class StudyPlanController {

    private static final Logger log = LoggerFactory.getLogger(StudyPlanController.class);

    @Autowired
    private StudyPlanService studyPlanService;

    @Autowired
    private StudyPlanProducer studyPlanProducer;

    @Autowired
    private StudyPlanGenerateTaskMapper generateTaskMapper;

    /**
     * 获取指定日期的学习计划详情。
     */
    @GetMapping("/{date}")
    public Result getPlan(@PathVariable String date) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || !(currentUser instanceof User)) {
            return Result.error("401", "请先登录学生账号");
        }
        try {
            LocalDate localDate = LocalDate.parse(date);
            DailyStudyPlan plan = studyPlanService.getPlanByDate(currentUser.getId(), localDate);
            return Result.success(studyPlanService.buildPlanResponse(plan));
        } catch (DateTimeParseException e) {
            return Result.error("日期格式错误,应为 yyyy-MM-dd");
        }
    }

    /**
     * 同步生成今日计划（已不推荐，前端请改用 generate-async）。
     * @deprecated 建议改用 POST /study-plan/generate-async
     */
    @PostMapping("/generate")
    public Result generatePlan(@RequestBody Map<String, String> body) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || !(currentUser instanceof User)) {
            return Result.error("401", "请先登录学生账号");
        }
        String feedback = body.get("feedback");
        try {
            DailyStudyPlan plan = studyPlanService.generatePlan(currentUser.getId(), feedback);
            return Result.success(studyPlanService.buildPlanResponse(plan));
        } catch (CustomException e) {
            return Result.error(e.getCode(), e.getMsg());
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        } catch (Exception e) {
            log.error("生成计划失败,userId={}", currentUser.getId(), e);
            return Result.error("生成计划失败,请稍后重试");
        }
    }

    /**
     * 异步生成今日计划：立即返回 taskId，由 RabbitMQ 消费者后台执行生成逻辑。
     * 前端拿到 taskId 后通过 GET /study-plan/generate-status/{taskId} 轮询状态。
     */
    @PostMapping("/generate-async")
    public Result generatePlanAsync(@RequestBody Map<String, String> body) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || !(currentUser instanceof User)) {
            return Result.error("401", "请先登录学生账号");
        }

        String feedback = body.get("feedback");
        String taskId = UUID.randomUUID().toString();
        LocalDateTime now = LocalDateTime.now();

        // 创建任务记录，初始状态 PENDING
        StudyPlanGenerateTask task = new StudyPlanGenerateTask();
        task.setTaskId(taskId);
        task.setUserId(currentUser.getId());
        task.setStatus("PENDING");
        task.setMessage("任务已提交，等待处理...");
        task.setFeedback(feedback);
        task.setCreatedTime(now);
        task.setUpdatedTime(now);
        generateTaskMapper.insert(task);

        // 投递 MQ 消息
        studyPlanProducer.sendGenerateTask(
                new StudyPlanGenerateMessage(taskId, currentUser.getId(), feedback));

        log.info("[Controller] 异步生成任务已提交 taskId={} userId={}", taskId, currentUser.getId());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("taskId", taskId);
        result.put("status", "PENDING");
        result.put("message", "任务已提交，等待处理...");
        return Result.success(result);
    }

    /**
     * 查询异步生成任务状态。
     * 状态：PENDING / RUNNING / SUCCESS / FAILED
     */
    @GetMapping("/generate-status/{taskId}")
    public Result getGenerateStatus(@PathVariable String taskId) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || !(currentUser instanceof User)) {
            return Result.error("401", "请先登录学生账号");
        }

        StudyPlanGenerateTask task = generateTaskMapper.selectByTaskId(taskId);
        if (task == null) {
            return Result.error("任务不存在");
        }
        // 安全校验：只能查询自己的任务
        if (!currentUser.getId().equals(task.getUserId())) {
            return Result.error("401", "无权查询此任务");
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("taskId", task.getTaskId());
        result.put("status", task.getStatus());
        result.put("message", task.getMessage());
        // 成功后附带计划数据，前端无需额外再请求
        if ("SUCCESS".equals(task.getStatus())) {
            try {
                DailyStudyPlan plan = studyPlanService.getPlanByDate(currentUser.getId(), LocalDate.now());
                result.put("plan", studyPlanService.buildPlanResponse(plan));
            } catch (Exception e) {
                log.warn("[Controller] 查询任务成功但读取计划失败 taskId={}", taskId, e);
            }
        }
        return Result.success(result);
    }

    /**
     * 撤回（删除）指定日期的学习计划。
     */
    @DeleteMapping("/{date}")
    public Result deletePlan(@PathVariable String date) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || !(currentUser instanceof User)) {
            return Result.error("401", "请先登录学生账号");
        }
        try {
            LocalDate localDate = LocalDate.parse(date);
            studyPlanService.deletePlan(currentUser.getId(), localDate);
            return Result.success();
        } catch (DateTimeParseException e) {
            return Result.error("日期格式错误,应为 yyyy-MM-dd");
        }
    }

    /**
     * 手动新增一条任务到指定日期的计划中。
     */
    @PostMapping("/{date}/tasks")
    public Result addTask(@PathVariable String date, @RequestBody Map<String, String> body) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || !(currentUser instanceof User)) {
            return Result.error("401", "请先登录学生账号");
        }
        try {
            LocalDate localDate = LocalDate.parse(date);
            return Result.success(studyPlanService.addTask(
                    currentUser.getId(),
                    localDate,
                    body.get("subject"),
                    body.get("content")));
        } catch (DateTimeParseException e) {
            return Result.error("日期格式错误,应为 yyyy-MM-dd");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 修改指定任务的科目与内容。
     */
    @PutMapping("/{date}/tasks/{taskId}")
    public Result updateTask(@PathVariable String date, @PathVariable String taskId,
            @RequestBody Map<String, String> body) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || !(currentUser instanceof User)) {
            return Result.error("401", "请先登录学生账号");
        }
        try {
            LocalDate localDate = LocalDate.parse(date);
            return Result.success(studyPlanService.updateTask(
                    currentUser.getId(),
                    localDate,
                    taskId,
                    body.get("subject"),
                    body.get("content")));
        } catch (DateTimeParseException e) {
            return Result.error("日期格式错误,应为 yyyy-MM-dd");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 删除指定任务。
     */
    @DeleteMapping("/{date}/tasks/{taskId}")
    public Result deleteTask(@PathVariable String date, @PathVariable String taskId) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || !(currentUser instanceof User)) {
            return Result.error("401", "请先登录学生账号");
        }
        try {
            LocalDate localDate = LocalDate.parse(date);
            studyPlanService.deleteTask(currentUser.getId(), localDate, taskId);
            return Result.success();
        } catch (DateTimeParseException e) {
            return Result.error("日期格式错误,应为 yyyy-MM-dd");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 将指定任务标记为已完成。
     */
    @PutMapping("/{date}/tasks/{taskId}/complete")
    public Result completeTask(@PathVariable String date, @PathVariable String taskId) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || !(currentUser instanceof User)) {
            return Result.error("401", "请先登录学生账号");
        }
        try {
            LocalDate localDate = LocalDate.parse(date);
            return Result.success(studyPlanService.updateTaskCompleted(currentUser.getId(), localDate, taskId, true));
        } catch (DateTimeParseException e) {
            return Result.error("日期格式错误,应为 yyyy-MM-dd");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 将指定任务从已完成恢复为未完成。
     */
    @PutMapping("/{date}/tasks/{taskId}/uncomplete")
    public Result uncompleteTask(@PathVariable String date, @PathVariable String taskId) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || !(currentUser instanceof User)) {
            return Result.error("401", "请先登录学生账号");
        }
        try {
            LocalDate localDate = LocalDate.parse(date);
            return Result.success(studyPlanService.updateTaskCompleted(currentUser.getId(), localDate, taskId, false));
        } catch (DateTimeParseException e) {
            return Result.error("日期格式错误,应为 yyyy-MM-dd");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 顺延任务到次日。
     */
    @PostMapping("/{date}/tasks/rollover")
    public Result rolloverTasks(@PathVariable String date,
            @RequestBody(required = false) Map<String, List<String>> body) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || !(currentUser instanceof User)) {
            return Result.error("401", "请先登录学生账号");
        }
        try {
            LocalDate localDate = LocalDate.parse(date);
            List<String> onlyTaskIds = body == null ? null : body.get("onlyTaskIds");
            return Result.success(studyPlanService.rolloverTasks(currentUser.getId(), localDate, onlyTaskIds));
        } catch (DateTimeParseException e) {
            return Result.error("日期格式错误,应为 yyyy-MM-dd");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }
}
