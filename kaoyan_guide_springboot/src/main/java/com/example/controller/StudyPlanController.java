package com.example.controller;

import com.example.common.Result;
import com.example.entity.Account;
import com.example.entity.DailyStudyPlan;
import com.example.entity.User;
import com.example.service.StudyPlanService;
import com.example.utils.TokenUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/study-plan")
public class StudyPlanController {

    @Autowired
    private StudyPlanService studyPlanService;

    /**
     * 获取指定日期的计划
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
            return Result.error("日期格式错误，应为 yyyy-MM-dd");
        }
    }

    /**
     * 生成今日计划
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
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("生成计划失败，请稍后重试");
        }
    }

    /**
     * 撤回（删除）指定日期的计划
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
            return Result.error("日期格式错误，应为 yyyy-MM-dd");
        }
    }

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
            return Result.error("日期格式错误，应为 yyyy-MM-dd");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

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
            return Result.error("日期格式错误，应为 yyyy-MM-dd");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

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
            return Result.error("日期格式错误，应为 yyyy-MM-dd");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

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
            return Result.error("日期格式错误，应为 yyyy-MM-dd");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

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
            return Result.error("日期格式错误，应为 yyyy-MM-dd");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

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
            return Result.error("日期格式错误，应为 yyyy-MM-dd");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }
}
