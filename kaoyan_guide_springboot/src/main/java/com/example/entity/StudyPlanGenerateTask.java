package com.example.entity;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 学习计划异步生成任务状态记录
 */
@Data
public class StudyPlanGenerateTask {

    private Long id;

    /** 任务唯一标识（UUID） */
    private String taskId;

    /** 发起任务的用户ID */
    private Integer userId;

    /** 任务状态: PENDING / RUNNING / SUCCESS / FAILED */
    private String status;

    /** 面向用户的状态描述文案 */
    private String message;

    /** 用户昨日反馈内容 */
    private String feedback;

    /** 失败时的错误原因（内部使用） */
    private String errorInfo;

    private LocalDateTime createdTime;

    private LocalDateTime updatedTime;
}
