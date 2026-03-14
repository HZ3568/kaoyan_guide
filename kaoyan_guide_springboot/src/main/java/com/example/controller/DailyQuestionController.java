package com.example.controller;

import com.example.common.Result;
import com.example.entity.Account;
import com.example.entity.Question;
import com.example.entity.QuestionRecord;
import com.example.service.DailyQuestionService;
import com.example.utils.TokenUtils;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/daily-question")
public class DailyQuestionController {

    @Resource
    private DailyQuestionService dailyQuestionService;

    @GetMapping("/today")
    public Result getTodayQuestion() {
        LocalDate today = LocalDate.now();
        Question question = dailyQuestionService.resolveTodayQuestion(today);
        if (question == null) {
            return Result.error("暂无可用题目");
        }
        Map<String, Object> data = new HashMap<>();
        data.put("question", dailyQuestionService.buildQuestionView(question));

        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser != null && currentUser.getId() != null) {
            QuestionRecord record = dailyQuestionService.getUserRecord(currentUser.getId().longValue(), today);
            if (record != null) {
                data.put("hasAnswered", true);
                data.put("answerResult", dailyQuestionService.buildAnswerResult(
                        question,
                        record.getUserAnswer(),
                        record.getIsCorrect() != null && record.getIsCorrect() == 1));
            } else {
                data.put("hasAnswered", false);
            }
        } else {
            data.put("hasAnswered", false);
        }
        return Result.success(data);
    }

    @PostMapping("/submit")
    public Result submitTodayAnswer(@RequestBody Map<String, String> body) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || currentUser.getId() == null) {
            return Result.error("401", "请先登录");
        }
        String answer = body.get("answer");
        if (answer == null || answer.trim().isEmpty()) {
            return Result.error("请先填写答案");
        }
        try {
            Map<String, Object> result = dailyQuestionService.submit(currentUser.getId().longValue(), answer.trim());
            return Result.success(result);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }
}
