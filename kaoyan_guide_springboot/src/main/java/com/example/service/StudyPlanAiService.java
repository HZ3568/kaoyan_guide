package com.example.service;

import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;
import dev.langchain4j.service.spring.AiService;

@AiService(chatModel = "openAiChatModel")
public interface StudyPlanAiService {

    @UserMessage("你是一位专业的考研学习规划师。请根据考生前3天的学习记录和昨天的真实学习反馈，为他制定今天的学习规划。\n" +
            "\n" +
            "【前3天历史记录】：\n" +
            "{{history}}\n" +
            "\n" +
            "【考生昨日反馈及当前状态】：\n" +
            "\"{{feedback}}\"\n" +
            "\n" +
            "请严格按照以下 JSON 格式输出你的规划结果，不要包含任何多余的解释性文字或 Markdown 标记：\n" +
            "{\n" +
            "  \"advice\": \"这里填写针对该考生当前状态的一段鼓励与调整建议（约100字）。如果他昨天没完成，请给出调整心态的建议；如果完成得好，请鼓励并适当推进进度。\",\n" +
            "  \"tasks\": [\n" +
            "    {\n" +
            "      \"taskId\": \"留空字符串即可\",\n" +
            "      \"subject\": \"科目名称，例如：数学、英语、408专业课等\",\n" +
            "      \"content\": \"具体的学习任务，例如：完成高数第二章课后习题并核对答案\",\n" +
            "      \"completed\": false\n" +
            "    },\n" +
            "    {\n" +
            "      \"taskId\": \"\",\n" +
            "      \"subject\": \"...\",\n" +
            "      \"content\": \"...\",\n" +
            "      \"completed\": false\n" +
            "    }\n" +
            "  ]\n" +
            "}")
    String generatePlan(@V("history") String history, @V("feedback") String feedback);
}
