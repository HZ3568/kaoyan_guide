package com.example.controller;

import com.example.entity.Account;
import com.example.entity.ExamResult;
import com.example.service.ExamResultService;
import com.example.utils.TokenUtils;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/exam")
public class ExamResultController {

    private final ExamResultService service;

    public ExamResultController(ExamResultService service) {
        this.service = service;
    }

    @PostMapping("/saveResult")
    public Map<String, Object> saveResult(@RequestBody Map<String, Object> payload) {
        Map<String, Object> response = new HashMap<>();

        try {
            Account currentUser = TokenUtils.getCurrentUser();

            Integer idInt = currentUser.getId();
            Long userId = idInt.longValue();

            String subject = (String) payload.get("subject");

            Number scoreNum = (Number) payload.get("score");
            Number durationNum = (Number) payload.get("duration");

            Integer score = scoreNum != null ? scoreNum.intValue() : null;
            Integer duration = durationNum != null ? durationNum.intValue() : null;

            System.out.println("userId: " + userId);
            System.out.println("subject: " + subject);
            System.out.println("score: " + score);
            System.out.println("duration: " + duration);

            if (userId == null || subject == null || score == null || duration == null) {
                response.put("code", "400");
                response.put("msg", "缺少参数");
                return response;
            }

            ExamResult result = new ExamResult();
            result.setUserId(userId);
            result.setSubject(subject);
            result.setScore(score);
            result.setDurationSeconds(duration);
            result.setCreateTime(LocalDateTime.now());

            service.saveResult(result);

            response.put("code", "200");
            response.put("msg", "保存成功");
        } catch (Exception e) {
            e.printStackTrace();
            response.put("code", "500");
            response.put("msg", "服务器错误");
        }

        return response;
    }


    @GetMapping("/list")
    public Map<String, Object> list(@RequestParam Long userId) {
        Map<String, Object> response = new HashMap<>();
        try {
            List<ExamResult> results = service.getUserResults(userId);
            response.put("code", "200");
            response.put("msg", "查询成功");
            response.put("data", results);
        } catch (Exception e) {
            e.printStackTrace();
            response.put("code", "500");
            response.put("msg", "服务器错误");
        }
        return response;
    }
}
