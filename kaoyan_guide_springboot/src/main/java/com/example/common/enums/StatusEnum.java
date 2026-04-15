package com.example.common.enums;

/**
 * 账号状态枚举
 * 1: 正常（可登录）
 * 0: 禁用（不可登录）
 */
public enum StatusEnum {
    DISABLED(0, "已禁用"),
    NORMAL(1, "正常");

    private final Integer code;
    private final String description;

    StatusEnum(Integer code, String description) {
        this.code = code;
        this.description = description;
    }

    public Integer code() {
        return code;
    }

    public String description() {
        return description;
    }

    public static StatusEnum fromCode(Integer code) {
        if (code == null) return null;
        for (StatusEnum status : values()) {
            if (status.code.equals(code)) {
                return status;
            }
        }
        return null;
    }
}
