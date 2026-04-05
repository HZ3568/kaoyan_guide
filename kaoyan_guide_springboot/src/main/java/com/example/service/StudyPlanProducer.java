package com.example.service;

import com.example.common.config.RabbitMQConfig;
import com.example.entity.StudyPlanGenerateMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class StudyPlanProducer {

    private static final Logger log = LoggerFactory.getLogger(StudyPlanProducer.class);

    @Autowired
    private RabbitTemplate rabbitTemplate;

    /**
     * 将学习计划生成任务消息投递到 RabbitMQ。
     */
    public void sendGenerateTask(StudyPlanGenerateMessage message) {
        log.info("[MQ] 投递生成任务 taskId={} userId={}", message.getTaskId(), message.getUserId());
        rabbitTemplate.convertAndSend(
                RabbitMQConfig.STUDY_PLAN_EXCHANGE,
                RabbitMQConfig.STUDY_PLAN_ROUTING_KEY,
                message);
    }
}
