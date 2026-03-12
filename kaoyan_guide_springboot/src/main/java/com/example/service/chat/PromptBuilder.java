package com.example.service.chat;

import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class PromptBuilder {
    public PromptAssembly build(int historyCount, boolean includeRag, List<String> selectedTools, String promptResource) {
        List<String> contextParts = new ArrayList<>();
        contextParts.add("system");
        for (int i = 0; i < historyCount; i++) {
            contextParts.add("history");
        }
        contextParts.add("current");
        if (includeRag) {
            contextParts.add("rag");
        }
        for (int i = 0; i < selectedTools.size(); i++) {
            contextParts.add("tool");
        }
        return new PromptAssembly(contextParts.size(), contextParts, promptResource);
    }
}
