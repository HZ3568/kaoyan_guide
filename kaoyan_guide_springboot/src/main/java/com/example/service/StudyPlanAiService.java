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
 * <p>
 * 优化要点：
 * 1. 使用专用 studyPlanChatModel（已配置 response_format=json_object）
 * 2. 不打印完整 prompt/response，只记录长度和耗时
 * 3. 保留 JSON 清洗兜底逻辑，应对模型偶发脏格式
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
     * 只打印关键耗时和长度，不打印完整 prompt / 响应正文，避免日志 I/O 拖慢请求。
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
     * <p>
     * 优化要点：
     * 1. 固定前缀部分（系统角色、输出格式要求）可为后续接入 Context Cache 预留扩展点
     * 2. 动态内容部分（历史摘要、用户反馈）保持精简，减少 token 消耗
     * <p>
     * Context Cache 扩展建议（阿里云百炼支持）：
     * - 固定前缀（SYSTEM_PROMPT_PREFIX）可标记为 cache，5分钟内复用
     * - 动态内容每次请求不同，不适合缓存
     * - 接入方式：在 ChatRequest 中添加 cache 相关参数（需 LangChain4j 支持）
     */
    public String buildPrompt(String history, String feedback) {
        // 固定前缀：系统角色 + 输出格式要求（后续可标记为 cache）
        String systemPromptPrefix = buildSystemPromptPrefix();

        // 动态内容：用户历史和反馈
        String dynamicContent = buildDynamicContent(history, feedback);

        return systemPromptPrefix + "\n" + dynamicContent;
    }

    /**
     * 固定前缀部分：系统角色定义 + JSON 格式要求。
     * <p>
     * 【Context Cache 扩展点】
     * 这部分内容在所有学习规划请求中都相同，适合标记为可缓存内容。
     * 阿里云百炼 Context Cache 可将此部分缓存 5 分钟，减少重复计算。
     * <p>
     * 接入方式（待 LangChain4j 支持）：
     * - 将此部分作为 SystemMessage 或标记为 cached content
     * - 在 ChatRequest 中设置 cache 参数
     */
    private String buildSystemPromptPrefix() {
        return "你是一位专业的考研学习规划师。请根据考生近期学习摘要和昨日反馈，为他制定今天的学习规划。\n"
                + "\n"
                + "请严格按以下 JSON 格式输出，不要包含任何多余文字或 Markdown：\n"
                + "{\"advice\":\"针对当前状态的具体建议（100-150字）\","
                + "\"tasks\":[{\"taskId\":\"\",\"subject\":\"科目\",\"content\":\"具体任务(25-40字之间)\",\"completed\":false}]}\n"
                + "\n"
                + "要求：tasks3-5项；科目分为政治，英语，数学和408，其中数学包括高等数学，线性代数和概率论，408包括数据结构、操作系统、计算机网络和计算机组成原理，因此数学和408的科目写小分类即可；确保当日提出的科目不能有重复";
    }

    /**
     * 动态内容部分：用户历史摘要 + 昨日反馈。
     * <p>
     * 这部分每次请求都不同，不适合缓存。
     */
    private String buildDynamicContent(String history, String feedback) {
        return "\n【近期学习摘要】：\n"
                + safeText(history)
                + "\n"
                + "【考生昨日反馈】：\n"
                + "\"" + safeText(feedback) + "\"";
    }

    private String safeText(String text) {
        return text == null ? "" : text.trim();
    }
}
