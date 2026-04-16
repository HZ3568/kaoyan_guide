package com.example.service;

import com.example.exception.CustomException;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.request.ChatRequest;
import dev.langchain4j.model.chat.response.ChatResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 学习规划 AI 服务。
 *
 * 优化策略：
 * 1. 用 prompt 本身约束 JSON 输出（不用 response_format 强制参数，避免模型不兼容返回错误）
 * 2. prompt 结构精简，避免过长输入拖慢模型
 * 3. 异常处理打印详细诊断（HTTP 状态码、响应 Content-Type、耗时）
 * 4. 超时时间充足（180s），不允许 retry 叠加耗时
 */
@Service
public class StudyPlanAiService {

    private static final Logger log = LoggerFactory.getLogger(StudyPlanAiService.class);
    private final ChatModel studyPlanChatModel;

    public StudyPlanAiService(@Qualifier("studyPlanChatModel") ChatModel studyPlanChatModel) {
        this.studyPlanChatModel = studyPlanChatModel;
    }

    /**
     * 调用大模型生成学习计划原始文本（期望为 JSON）。
     */
    public String generatePlan(String finalPrompt) {
        long startTime = System.currentTimeMillis();
        log.info("[AI] 开始调用，promptLen={}", finalPrompt.length());

        try {
            ChatRequest request = ChatRequest.builder()
                    .messages(List.of(UserMessage.from(finalPrompt)))
                    .build();
            ChatResponse response = studyPlanChatModel.chat(request);

            long duration = System.currentTimeMillis() - startTime;

            if (response == null || response.aiMessage() == null || response.aiMessage().text() == null) {
                log.warn("[AI] 返回空响应，耗时={}ms", duration);
                throw new CustomException("500", "AI 未返回有效学习计划，请重试");
            }

            String aiResponse = response.aiMessage().text();
            log.info("[AI] 调用成功，耗时={}ms responseLen={}", duration, aiResponse.length());
            return aiResponse;

        } catch (CustomException e) {
            throw e;
        } catch (Exception e) {
            long duration = System.currentTimeMillis() - startTime;
            log.error("[AI] 调用失败，耗时={}ms exceptionType={} message={}", duration, e.getClass().getName(), e.getMessage());

            // 打印更详细的诊断信息
            Throwable rootCause = getRootCause(e);
            String rootCauseType = rootCause.getClass().getSimpleName();
            log.error("[AI] 根因类型={} 消息={}", rootCauseType, rootCause.getMessage());

            if (rootCauseType.contains("Timeout") || rootCauseType.contains("SocketTimeout")) {
                throw new CustomException("504", "AI 生成学习计划超时（模型响应太慢），请稍后重试或联系管理员");
            } else if (rootCauseType.contains("Connect") || rootCauseType.contains("Network")) {
                throw new CustomException("503", "网络连接失败，请检查网络后重试");
            } else if (e.getMessage() != null && e.getMessage().contains("content too long")) {
                throw new CustomException("400", "输入内容过长，请精简后重试");
            } else if (e.getMessage() != null && e.getMessage().contains("application/octet-stream")) {
                throw new CustomException("500", "AI 返回格式异常，请稍后重试");
            } else {
                throw new CustomException("500", "学习计划生成失败，请稍后再试");
            }
        }
    }

    private Throwable getRootCause(Throwable throwable) {
        Throwable cause = throwable;
        while (cause.getCause() != null && cause.getCause() != cause) {
            cause = cause.getCause();
        }
        return cause;
    }

    /**
     * 组装学习规划提示词。
     * 通过 prompt 本身约束 JSON 输出，不依赖模型的 response_format 参数（避免兼容性问题）。
     */
    public String buildPrompt(String history, String feedback) {
        String systemPromptPrefix = buildSystemPromptPrefix();
        String dynamicContent = buildDynamicContent(history, feedback);
        return systemPromptPrefix + "\n" + dynamicContent;
    }

    /**
     * 固定前缀：系统角色定义 + JSON 格式要求。
     * 用 prompt 强制约束 JSON，不依赖模型 response_format 能力。
     */
    private String buildSystemPromptPrefix() {
        return "你是一位考研学习规划师。根据考生近期学习情况和昨日反馈，制定今日学习计划。\n\n"
                + "【输出格式】仅输出JSON，无任何解释：\n"
                + "{\"advice\":\"建议（限50字）\","
                + "\"tasks\":[{\"taskId\":\"1\",\"subject\":\"科目\",\"content\":\"任务（限25字）\",\"completed\":false}]}\n\n"
                + "【约束】固定4条任务，科目为政治/英语/数学/408，content限25字，advice限50字，只输出JSON";
    }

    /**
     * 动态内容：用户历史摘要 + 昨日反馈。
     */
    private String buildDynamicContent(String history, String feedback) {
        return "【近期学习】\n" + safeText(history) + "\n\n【昨日反馈】" + safeText(feedback);
    }

    private String safeText(String text) {
        return text == null ? "" : text.trim();
    }
}
