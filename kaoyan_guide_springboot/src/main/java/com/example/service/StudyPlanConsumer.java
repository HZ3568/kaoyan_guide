package com.example.service;

import com.example.common.config.RabbitMQConfig;
import com.example.entity.StudyPlanGenerateMessage;
import com.example.mapper.StudyPlanGenerateTaskMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class StudyPlanConsumer {

    private static final Logger log = LoggerFactory.getLogger(StudyPlanConsumer.class);

    @Autowired
    private StudyPlanGenerateTaskMapper generateTaskMapper;

    @Autowired
    private StudyPlanService studyPlanService;

    /**
     * 消费学习计划生成任务消息。
     * 幂等保护：若任务已是 SUCCESS 或 RUNNING，跳过重复消费。
     */
    @RabbitListener(queues = RabbitMQConfig.STUDY_PLAN_QUEUE)
    public void handleGenerateTask(StudyPlanGenerateMessage message) {
        String taskId = message.getTaskId();
        Integer userId = message.getUserId();
        log.info("[Consumer] 收到生成任务 taskId={} userId={}", taskId, userId);

        // 幂等检查：已成功或正在执行则跳过
        var existingTask = generateTaskMapper.selectByTaskId(taskId);
        if (existingTask == null) {
            log.warn("[Consumer] 任务记录不存在，忽略 taskId={}", taskId);
            return;
        }
        String currentStatus = existingTask.getStatus();
        if ("SUCCESS".equals(currentStatus) || "RUNNING".equals(currentStatus)) {
            log.warn("[Consumer] 任务已处于 {} 状态，跳过重复消费 taskId={}", currentStatus, taskId);
            return;
        }

        // 更新为 RUNNING
        generateTaskMapper.updateStatus(taskId, "RUNNING", "正在生成今日学习计划...", null, LocalDateTime.now());

        try {
            studyPlanService.generatePlanInternal(userId, message.getFeedback());

            generateTaskMapper.updateStatus(taskId, "SUCCESS", "学习计划已生成", null, LocalDateTime.now());
            log.info("[Consumer] 任务完成 taskId={} userId={}", taskId, userId);

        } catch (Exception e) {
            String errorMsg = e.getMessage() != null ? e.getMessage() : e.getClass().getSimpleName();
            log.error("[Consumer] 任务失败 taskId={} userId={} error={}", taskId, userId, errorMsg, e);
            generateTaskMapper.updateStatus(taskId, "FAILED", "生成失败：" + errorMsg, errorMsg, LocalDateTime.now());
        }
    }
}
