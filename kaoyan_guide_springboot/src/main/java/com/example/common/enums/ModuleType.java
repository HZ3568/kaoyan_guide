package com.example.common.enums;

public enum ModuleType {
    LEARNING_PLAN("learning_plan"),
    CONSULT_COLLEGE("consult_college");

    private final String code;

    ModuleType(String code) {
        this.code = code;
    }

    public String getCode() {
        return code;
    }

    public static ModuleType fromCode(String code) {
        if (code == null) {
            throw new IllegalArgumentException("moduleType不能为空");
        }
        for (ModuleType value : values()) {
            if (value.code.equalsIgnoreCase(code.trim())) {
                return value;
            }
        }
        throw new IllegalArgumentException("不支持的moduleType: " + code);
    }
}
