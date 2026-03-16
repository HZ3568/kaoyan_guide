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

    /**
     * 注入学习规划使用的对话模型。
     */
    public StudyPlanAiService(@Qualifier("openAiChatModel") ChatModel openAiChatModel) {
        this.openAiChatModel = openAiChatModel;
    }

    /**
     * 调用大模型生成学习计划原始文本（期望为 JSON）。
     * 当模型返回为空时，兜底为 "{}" 避免上游空指针。
     */
    public String generatePlan(String finalPrompt) {
        long startTime = System.currentTimeMillis();
        log.info("开始调用 AI 生成学习计划，prompt 长度: {}", finalPrompt.length());

        try {
            ChatRequest request = ChatRequest.builder()
                    .messages(List.of(UserMessage.from(finalPrompt)))
                    .build();
            ChatResponse response = openAiChatModel.chat(request);

            long duration = System.currentTimeMillis() - startTime;
            log.info("AI 调用成功，耗时: {} ms", duration);

            if (response == null || response.aiMessage() == null || response.aiMessage().text() == null) {
                log.warn("AI 返回空响应");
                throw new CustomException("500", "AI 未返回有效学习计划，请重试");
            }
            return response.aiMessage().text();

        } catch (CustomException e) {
            // 直接抛出已经包装好的 CustomException
            throw e;
        } catch (Exception e) {
            long duration = System.currentTimeMillis() - startTime;
            log.error("AI 调用失败，耗时: {} ms，异常类型: {}", duration, e.getClass().getName(), e);

            // 递归提取根因
            Throwable rootCause = getRootCause(e);
            String rootCauseType = rootCause.getClass().getSimpleName();

            // 根据异常类型返回友好提示
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

    /**
     * 递归提取异常根因
     */
    private Throwable getRootCause(Throwable throwable) {
        Throwable cause = throwable;
        while (cause.getCause() != null && cause.getCause() != cause) {
            cause = cause.getCause();
        }
        return cause;
    }

    /**
     * 组装学习规划提示词。
     * 核心约束：仅输出 JSON，且内容聚焦学习任务，不引入院校咨询信息。
     */
    public String buildPrompt(String history, String feedback) {
        return "你是一位专业的考研学习规划师。请根据考生前3天的学习记录和昨天的真实学习反馈，为他制定今天的学习规划。\n"
                + "\n"
                + "【前3天历史记录】：\n"
                + safeText(history)
                + "\n"
                + "\n"
                + "【考生昨日反馈及当前状态】：\n"
                + "\"" + safeText(feedback) + "\"\n"
                + "\n"
                + "请仅根据上述学习记录和反馈生成计划，不要引入任何院校咨询、院校分数、咨询服务等无关信息。\n"
                + "请严格按照以下 JSON 格式输出你的规划结果，不要包含任何多余的解释性文字或 Markdown 标记：\n"
                + "{\n"
                + "  \"advice\": \"针对该考生当前状态的一段简短建议（50-80字）。如果昨天没完成，给出调整建议；如果完成得好，鼓励并推进进度。\",\n"
                + "  \"tasks\": [\n"
                + "    {\n"
                + "      \"taskId\": \"\",\n"
                + "      \"subject\": \"科目名称（如：数学、英语、政治、408专业课）\",\n"
                + "      \"content\": \"具体学习任务（简洁明确，20字以内）\",\n"
                + "      \"completed\": false\n"
                + "    }\n"
                + "  ]\n"
                + "}\n"
                + "\n"
                + "要求：\n"
                + "1. advice 字段控制在 50-80 字，简洁实用\n"
                + "2. tasks 数组包含 3-5 个任务即可，不要过多\n"
                + "3. 每个任务的 content 字段控制在 20 字以内，清晰明确\n"
                + "4. 任务要具体可执行，避免空泛描述";
    }

    /**
     * 文本安全处理：null 转空串并去除首尾空白。
     */
    private String safeText(String text) {
        if (text == null) {
            return "";
        }
        return text.trim();
    }
}
