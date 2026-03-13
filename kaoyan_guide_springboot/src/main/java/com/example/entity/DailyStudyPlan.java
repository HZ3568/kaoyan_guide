package com.example.entity;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class DailyStudyPlan {
    /**
     * 主键
     */
    private Long id;

    /**
     * 用户ID
     */
    private Integer userId;

    /**
     * 计划日期
     */
    private LocalDate planDate;

    /**
     * 用户反馈（昨日总结/当前状态）
     */
    private String userFeedback;

    /**
     * AI建议
     */
    private String aiAdvice;

    /**
     * 计划状态：PENDING/GENERATED
     */
    private String planStatus;

    /**
     * 每日任务列表（JSON字符串）
     */
    private String dailyTasks;

    /**
     * 创建时间
     */
    private LocalDateTime createTime;

    /**
     * 更新时间
     */
    private LocalDateTime updateTime;
}
