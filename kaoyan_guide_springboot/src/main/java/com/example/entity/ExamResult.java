package com.example.entity;

import java.time.LocalDateTime;

public class ExamResult {
    private Long id;
    private Long userId;
    private String subject;
    private String questionSource;   // 试题出处（新增）
    private Integer score;
    private Integer durationSeconds;
    private String simulationMode;   // 模拟模式（新增）
    private LocalDateTime createTime;

    // ===== Getter & Setter =====
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getSubject() { return subject; }
    public void setSubject(String subject) { this.subject = subject; }

    public String getQuestionSource() { return questionSource; }
    public void setQuestionSource(String questionSource) { this.questionSource = questionSource; }

    public Integer getScore() { return score; }
    public void setScore(Integer score) { this.score = score; }

    public Integer getDurationSeconds() { return durationSeconds; }
    public void setDurationSeconds(Integer durationSeconds) { this.durationSeconds = durationSeconds; }

    public String getSimulationMode() { return simulationMode; }
    public void setSimulationMode(String simulationMode) { this.simulationMode = simulationMode; }

    public LocalDateTime getCreateTime() { return createTime; }
    public void setCreateTime(LocalDateTime createTime) { this.createTime = createTime; }
}
