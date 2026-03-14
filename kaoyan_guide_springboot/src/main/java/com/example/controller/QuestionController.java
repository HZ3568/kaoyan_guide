package com.example.controller;

import com.example.common.Result;
import com.example.entity.Question;
import com.example.service.QuestionService;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/question")
public class QuestionController {

    @Resource
    private QuestionService questionService;

    @PostMapping("/add")
    public Result add(@RequestBody Question question) {
        questionService.add(question);
        return Result.success();
    }

    @PutMapping("/update")
    public Result update(@RequestBody Question question) {
        questionService.updateById(question);
        return Result.success();
    }

    @DeleteMapping("/delete/{id}")
    public Result delete(@PathVariable Long id) {
        questionService.deleteById(id);
        return Result.success();
    }

    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Long> ids) {
        questionService.deleteBatch(ids);
        return Result.success();
    }

    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Long id) {
        Question question = questionService.selectById(id);
        return Result.success(question);
    }

    @GetMapping("/selectAll")
    public Result selectAll(Question question) {
        List<Question> list = questionService.selectAll(question);
        return Result.success(list);
    }

    @GetMapping("/selectPage")
    public Result selectPage(Question question,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<Question> pageInfo = questionService.selectPage(question, pageNum, pageSize);
        return Result.success(pageInfo);
    }

    @PostMapping("/assignDaily")
    public Result assignDaily(@RequestBody Map<String, String> body) {
        String questionDateStr = body.get("questionDate");
        String questionIdStr = body.get("questionId");
        if (questionDateStr == null || questionDateStr.trim().isEmpty()) {
            return Result.error("请选择日期");
        }
        if (questionIdStr == null || questionIdStr.trim().isEmpty()) {
            return Result.error("请选择题目");
        }
        try {
            LocalDate questionDate = LocalDate.parse(questionDateStr);
            Long questionId = Long.parseLong(questionIdStr);
            questionService.assignDailyQuestion(questionDate, questionId);
            return Result.success();
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        } catch (Exception e) {
            return Result.error("参数格式不正确");
        }
    }

    @GetMapping("/dailyAssignments")
    public Result dailyAssignments(@RequestParam(required = false) String startDate,
                                   @RequestParam(required = false) String endDate) {
        LocalDate end = endDate == null || endDate.trim().isEmpty() ? LocalDate.now() : LocalDate.parse(endDate);
        LocalDate start = startDate == null || startDate.trim().isEmpty() ? end.minusDays(14) : LocalDate.parse(startDate);
        List<Map<String, Object>> assignments = questionService.selectRecentAssignments(start, end);
        Map<String, Object> data = new HashMap<>();
        data.put("list", assignments);
        return Result.success(data);
    }
}
