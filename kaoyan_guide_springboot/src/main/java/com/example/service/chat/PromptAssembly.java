package com.example.service.chat;

import java.util.List;

public class PromptAssembly {
    private final int messageCount;
    private final List<String> contextParts;
    private final String finalPromptSource;

    public PromptAssembly(int messageCount, List<String> contextParts, String finalPromptSource) {
        this.messageCount = messageCount;
        this.contextParts = contextParts;
        this.finalPromptSource = finalPromptSource;
    }

    public int getMessageCount() {
        return messageCount;
    }

    public List<String> getContextParts() {
        return contextParts;
    }

    public String getFinalPromptSource() {
        return finalPromptSource;
    }
}
