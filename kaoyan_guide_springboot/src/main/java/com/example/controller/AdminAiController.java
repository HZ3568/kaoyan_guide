package com.example.controller;

import com.example.common.Result;
import com.example.service.AdminAiService;
import com.github.pagehelper.PageInfo;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/admin/ai")
public class AdminAiController {

    private final AdminAiService service;

    public AdminAiController(AdminAiService service) {
        this.service = service;
    }

    // ==================== 咨询会话管理 ====================

    /**
     * 分页查询会话列表
     * @param userId 可选，按用户ID过滤
     * @param moduleType 可选，learning_plan / consult_college
     */
    @GetMapping("/session/list")
    public Result sessionList(
            @RequestParam(defaultValue = "1") int pageNum,
            @RequestParam(defaultValue = "10") int pageSize,
            @RequestParam(required = false) Integer userId,
            @RequestParam(required = false) String moduleType) {
        PageInfo<Map<String, Object>> page = service.getSessionList(pageNum, pageSize, userId, moduleType);
        return Result.success(page);
    }

    /**
     * 查看会话历史消息
     * @param memoryKey 从会话列表获取的 memoryKey
     */
    @GetMapping("/session/history")
    public Result sessionHistory(@RequestParam String memoryKey) {
        List<Map<String, Object>> history = service.getSessionHistory(memoryKey);
        return Result.success(history);
    }

    /**
     * 删除指定会话
     */
    @DeleteMapping("/session/delete")
    public Result deleteSession(@RequestParam String memoryKey) {
        service.deleteSession(memoryKey);
        return Result.success();
    }

    // ==================== 学习规划管理 ====================

    /**
     * 分页查询所有用户的学习计划
     */
    @GetMapping("/studyPlan/list")
    public Result studyPlanList(
            @RequestParam(defaultValue = "1") int pageNum,
            @RequestParam(defaultValue = "10") int pageSize,
            @RequestParam(required = false) Integer userId) {
        PageInfo<Map<String, Object>> page = service.getStudyPlanList(pageNum, pageSize, userId);
        return Result.success(page);
    }

    /**
     * 修改任务完成状态（管理员）
     */
    @PutMapping("/studyPlan/task/update")
    public Result updateTaskCompleted(
            @RequestParam Long planId,
            @RequestParam String taskId,
            @RequestParam Boolean completed) {
        boolean ok = service.updateTaskCompleted(planId, taskId, completed);
        return ok ? Result.success() : Result.error("更新失败");
    }

    /**
     * 删除指定任务（管理员）
     */
    @DeleteMapping("/studyPlan/task/delete")
    public Result deleteTask(
            @RequestParam Long planId,
            @RequestParam String taskId) {
        boolean ok = service.deleteTask(planId, taskId);
        return ok ? Result.success() : Result.error("删除失败");
    }

    /**
     * 删除整个学习计划（管理员）
     */
    @DeleteMapping("/studyPlan/plan/delete")
    public Result deletePlan(
            @RequestParam Integer userId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) String dateStr) {
        try {
            LocalDate date = LocalDate.parse(dateStr);
            service.deletePlan(userId, date);
            return Result.success();
        } catch (DateTimeParseException e) {
            return Result.error("日期格式错误，应为 yyyy-MM-dd");
        }
    }
}
