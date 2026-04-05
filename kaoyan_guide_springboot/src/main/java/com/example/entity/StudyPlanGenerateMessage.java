package com.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

/**
 * 投递到 RabbitMQ 的学习计划生成任务消息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class StudyPlanGenerateMessage implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 对应 study_plan_generate_task.task_id */
    private String taskId;

    /** 发起任务的用户ID */
    private Integer userId;

    /** 用户昨日反馈/今日心情（可为空） */
    private String feedback;
}
