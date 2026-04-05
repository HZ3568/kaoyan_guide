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

@Service
public class StudyPlanAiService {

    private static final Logger log = LoggerFactory.getLogger(StudyPlanAiService.class);
    private final ChatModel openAiChatModel;

    public StudyPlanAiService(@Qualifier("openAiChatModel") ChatModel openAiChatModel) {
        this.openAiChatModel = openAiChatModel;
    }

    /**
     * 调用大模型生成学习计划原始文本（期望为 JSON）。
     * 只打印关键耗时和长度，不打印完整 prompt / 响应正文，避免日志 I/O 拖慢请求。
     */
    public String generatePlan(String finalPrompt) {
        long startTime = System.currentTimeMillis();
        log.info("[AI] 开始调用，promptLen={}", finalPrompt.length());

        try {
            ChatRequest request = ChatRequest.builder()
                    .messages(List.of(UserMessage.from(finalPrompt)))
                    .build();
            ChatResponse response = openAiChatModel.chat(request);

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
            log.error("[AI] 调用失败，耗时={}ms exceptionType={}", duration, e.getClass().getName(), e);

            Throwable rootCause = getRootCause(e);
            String rootCauseType = rootCause.getClass().getSimpleName();

            if (rootCauseType.contains("Timeout") || rootCauseType.contains("SocketTimeout")) {
                throw new CustomException("504", "AI 生成学习计划超时，请稍后重试");
            } else if (rootCauseType.contains("Connect") || rootCauseType.contains("Network")) {
                throw new CustomException("503", "网络连接失败，请检查网络后重试");
            } else if (e.getMessage() != null && e.getMessage().contains("content too long")) {
                throw new CustomException("400", "输入内容过长，请精简后重试");
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
     * history 参数已是精简摘要（非完整 JSON），prompt 比原来更短。
     */
    public String buildPrompt(String history, String feedback) {
        return "你是一位专业的考研学习规划师。请根据考生近期学习摘要和昨日反馈，为他制定今天的学习规划。\n"
                + "\n"
                + "【近期学习摘要】：\n"
                + safeText(history)
                + "\n"
                + "【考生昨日反馈】：\n"
                + "\"" + safeText(feedback) + "\"\n"
                + "\n"
                + "请严格按以下 JSON 格式输出，不要包含任何多余文字或 Markdown：\n"
                + "{\"advice\":\"针对当前状态的简短建议（50-80字）\","
                + "\"tasks\":[{\"taskId\":\"\",\"subject\":\"科目\",\"content\":\"具体任务(20字内)\",\"completed\":false}]}\n"
                + "\n"
                + "要求：advice 50-80字；tasks 3-5项；每项 content 20字以内；任务具体可执行。";
    }

    private String safeText(String text) {
        return text == null ? "" : text.trim();
    }
}
