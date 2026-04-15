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
 * 1. 与通用 openAiChatModel 隔离，避免影响其他 AI 模块
 * 2. 使用 qwen-plus（完整版，非 flash 预览版），响应更快更稳定
 * 3. timeout 180s 充足，允许模型完整生成
 * 4. maxRetries 0，不允许 retry 叠加耗时
 * 5. 不使用 responseFormat("json_object")，改用 prompt 本身约束 JSON 输出
 */
@Configuration
public class StudyPlanAiConfig {

    @Value("${langchain4j.open-ai.study-plan-chat-model.base-url:${langchain4j.open-ai.chat-model.base-url}}")
    private String baseUrl;

    @Value("${langchain4j.open-ai.study-plan-chat-model.api-key:${langchain4j.open-ai.chat-model.api-key}}")
    private String apiKey;

    @Value("${langchain4j.open-ai.study-plan-chat-model.model-name:${langchain4j.open-ai.chat-model.model-name}}")
    private String modelName;

    @Value("${langchain4j.open-ai.study-plan-chat-model.timeout:180s}")
    private Duration timeout;

    @Value("${langchain4j.open-ai.study-plan-chat-model.max-retries:0}")
    private Integer maxRetries;

    @Value("${langchain4j.open-ai.study-plan-chat-model.max-tokens:800}")
    private Integer maxTokens;

    @Bean("studyPlanChatModel")
    public ChatModel studyPlanChatModel() {
        return OpenAiChatModel.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .modelName(modelName)
                .timeout(timeout)
                .maxRetries(maxRetries)
                .maxTokens(maxTokens)
                // 不使用 responseFormat("json_object")：该参数在部分模型版本上
                // 会导致模型返回错误格式（application/octet-stream），改由 prompt 约束 JSON
                .logRequests(false)
                .logResponses(false)
                .build();
    }
}
