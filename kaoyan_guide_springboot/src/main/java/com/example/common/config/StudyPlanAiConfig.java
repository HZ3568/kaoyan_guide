package com.example.common.config;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

/**
 * 学习规划模块专用 AI 模型配置。
 *
 * 设计目标：
 * 1. 与通用 openAiChatModel 隔离，避免影响其他 AI 模块（院校咨询、知识库等）
 * 2. 针对学习规划场景优化超时和重试策略，降低长尾等待
 * 3. 为后续切换更轻量、更快的模型预留扩展点
 *
 * 配置说明：
 * - timeout: 60s（学习规划是用户交互型请求，不应等待过久）
 * - max-retries: 0（失败快速返回，避免重试拖长总耗时）
 * - response-format: json_object（强制 JSON 输出，提高稳定性）
 */
@Configuration
public class StudyPlanAiConfig {

    @Value("${langchain4j.open-ai.study-plan-chat-model.base-url:${langchain4j.open-ai.chat-model.base-url}}")
    private String baseUrl;

    @Value("${langchain4j.open-ai.study-plan-chat-model.api-key:${langchain4j.open-ai.chat-model.api-key}}")
    private String apiKey;

    @Value("${langchain4j.open-ai.study-plan-chat-model.model-name:${langchain4j.open-ai.chat-model.model-name}}")
    private String modelName;

    @Value("${langchain4j.open-ai.study-plan-chat-model.timeout:60s}")
    private Duration timeout;

    @Value("${langchain4j.open-ai.study-plan-chat-model.max-retries:0}")
    private Integer maxRetries;

    @Value("${langchain4j.open-ai.study-plan-chat-model.max-tokens:2000}")
    private Integer maxTokens;

    /**
     * 学习规划专用 ChatModel Bean。
     *
     * 关键优化：
     * 1. responseFormat("json_object") - 强制模型输出 JSON，减少清洗和重试开销
     * 2. timeout 60s - 比通用模型的 120s 更短，快速失败
     * 3. maxRetries 0 - 不自动重试，避免一次慢请求拖得更久
     * 4. logRequests/logResponses false - 减少日志 I/O
     */
    @Bean("studyPlanChatModel")
    public ChatModel studyPlanChatModel() {
        return OpenAiChatModel.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .modelName(modelName)
                .timeout(timeout)
                .maxRetries(maxRetries)
                .maxTokens(maxTokens)
                .responseFormat("json_object")  // 阿里云百炼支持，强制 JSON 输出
                .logRequests(false)
                .logResponses(false)
                .build();
    }
}
