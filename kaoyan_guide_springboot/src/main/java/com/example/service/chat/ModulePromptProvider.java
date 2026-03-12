package com.example.service.chat;

import com.example.common.enums.ModuleType;

public interface ModulePromptProvider {
    ModuleType moduleType();

    String promptResource();
}
