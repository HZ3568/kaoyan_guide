package com.example.utils;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * 密码加密与校验工具类。
 * 使用 Spring Security BCrypt 算法，对密码进行单向哈希存储。
 * 登录时使用 matches() 方法比对输入与存储的哈希值。
 */
@Component
public class PasswordEncoder {

    private static final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

    /**
     * 对明文密码进行加密，返回哈希值。
     * 每次调用生成的哈希值不同（随机盐），但 matches() 比对结果一致。
     */
    public static String encode(String rawPassword) {
        return encoder.encode(rawPassword);
    }

    /**
     * 校验输入密码与存储的哈希值是否匹配。
     */
    public static boolean matches(String rawPassword, String encodedPassword) {
        return encoder.matches(rawPassword, encodedPassword);
    }
}
