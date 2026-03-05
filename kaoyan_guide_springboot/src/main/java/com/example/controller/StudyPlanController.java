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
            return Result.success(plan);
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
            return Result.success(plan);
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
}
