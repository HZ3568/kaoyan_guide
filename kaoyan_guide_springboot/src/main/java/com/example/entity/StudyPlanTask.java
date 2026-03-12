package com.example.entity;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class StudyPlanTask {
    private Long id;
    private String taskId;
    private Long planId;
    private String subject;
    private String content;
    private Boolean completed;
    private Integer sortNo;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
