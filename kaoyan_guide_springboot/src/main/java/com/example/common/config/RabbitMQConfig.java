package com.example.common.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    /** 学习计划生成任务队列名 */
    public static final String STUDY_PLAN_QUEUE = "study.plan.generate.queue";

    /** 学习计划生成任务交换机名 */
    public static final String STUDY_PLAN_EXCHANGE = "study.plan.generate.exchange";

    /** 路由键 */
    public static final String STUDY_PLAN_ROUTING_KEY = "study.plan.generate";

    @Bean
    public Queue studyPlanQueue() {
        // durable=true 保证 RabbitMQ 重启后队列不丢失
        return QueueBuilder.durable(STUDY_PLAN_QUEUE).build();
    }

    @Bean
    public DirectExchange studyPlanExchange() {
        return ExchangeBuilder.directExchange(STUDY_PLAN_EXCHANGE).durable(true).build();
    }

    @Bean
    public Binding studyPlanBinding(Queue studyPlanQueue, DirectExchange studyPlanExchange) {
        return BindingBuilder.bind(studyPlanQueue).to(studyPlanExchange).with(STUDY_PLAN_ROUTING_KEY);
    }

    /** 使用 JSON 序列化消息体，便于调试和跨服务查看 */
    @Bean
    public MessageConverter jsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory,
                                          MessageConverter jsonMessageConverter) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(jsonMessageConverter);
        return template;
    }
}
