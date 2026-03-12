package com.example.service.chat;

import com.example.common.enums.ModuleType;

import java.util.List;

public interface ModuleToolProvider {
    ModuleType moduleType();

    List<String> toolNames();
}
