package com.example.service.chat;

import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import org.springframework.stereotype.Component;

@Component
public class ChatOutputSanitizer {

    public String sanitize(String rawOutput) {
        if (rawOutput == null) {
            return "";
        }
        String cleanText = stripCodeFence(rawOutput.trim());
        if (!JSONUtil.isTypeJSON(cleanText)) {
            return cleanText;
        }
        try {
            if (JSONUtil.isTypeJSONObject(cleanText)) {
                JSONObject root = JSONUtil.parseObj(cleanText);
                String fromMessage = readMessageContent(root);
                if (fromMessage != null) {
                    return fromMessage;
                }
                String fromChoices = readChoicesMessageContent(root);
                if (fromChoices != null) {
                    return fromChoices;
                }
                String fromContent = root.getStr("content");
                if (fromContent != null) {
                    return fromContent;
                }
                return cleanText;
            }
            return cleanText;
        } catch (Exception e) {
            return cleanText;
        }
    }

    private String readMessageContent(JSONObject root) {
        Object message = root.get("message");
        if (message == null) {
            return null;
        }
        if (message instanceof JSONObject jsonMessage) {
            return jsonMessage.getStr("content");
        }
        if (message instanceof String textMessage && JSONUtil.isTypeJSONObject(textMessage)) {
            JSONObject nested = JSONUtil.parseObj(textMessage);
            return nested.getStr("content");
        }
        return null;
    }

    private String readChoicesMessageContent(JSONObject root) {
        Object choices = root.get("choices");
        if (!(choices instanceof JSONArray choiceArray) || choiceArray.isEmpty()) {
            return null;
        }
        Object firstChoice = choiceArray.get(0);
        if (!(firstChoice instanceof JSONObject choiceObj)) {
            return null;
        }
        Object message = choiceObj.get("message");
        if (!(message instanceof JSONObject messageObj)) {
            return null;
        }
        return messageObj.getStr("content");
    }

    private String stripCodeFence(String content) {
        String result = content.trim();
        if (result.startsWith("```json")) {
            result = result.substring(7).trim();
        } else if (result.startsWith("```")) {
            result = result.substring(3).trim();
        }
        if (result.endsWith("```")) {
            result = result.substring(0, result.length() - 3).trim();
        }
        return result;
    }
}
