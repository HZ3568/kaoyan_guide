package com.example.service;

import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.example.entity.DailyStudyPlan;
import com.example.mapper.StudyPlanMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

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
        return studyPlanMapper.selectByDate(userId, date);
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
        // 确保tasks是字符串格式存入数据库
        String tasks = jsonObject.get("tasks").toString();

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
}
