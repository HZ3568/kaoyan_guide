package com.example.controller;

import cn.hutool.captcha.CaptchaUtil;
import cn.hutool.captcha.LineCaptcha;
import com.example.common.Result;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/**
 * 图形验证码接口
 */
@RestController
public class CaptchaController {

    private static final String CAPTCHA_PREFIX = "captcha:";
    private static final long CAPTCHA_EXPIRE_SECONDS = 60L;

    private final StringRedisTemplate redisTemplate;

    public CaptchaController(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    /**
     * 生成验证码
     * 返回 uuid（前端提交登录时携带）和 base64 图片
     */
    @GetMapping("/captcha")
    public Result captcha() {
        // 生成 4 位数字字母验证码，图片宽 120 高 40，干扰线 30 条
        // 不指定字体，使用 hutool 默认字体，避免宿主机缺少字体
        LineCaptcha captcha = CaptchaUtil.createLineCaptcha(120, 40, 4, 30);

        String code = captcha.getCode();          // 真实验证码
        String uuid = UUID.randomUUID().toString(); // 唯一 key
        String redisKey = CAPTCHA_PREFIX + uuid;

        // 存入 Redis，60 秒过期
        redisTemplate.opsForValue().set(redisKey, code, CAPTCHA_EXPIRE_SECONDS, TimeUnit.SECONDS);

        // 生成图片 base64
        String base64Image = captcha.getImageBase64();

        Map<String, String> data = new HashMap<>();
        data.put("uuid", uuid);
        data.put("img", base64Image);
        return Result.success(data);
    }

    /**
     * 校验验证码（内部接口，供 WebController 调用）
     */
    public boolean validate(String uuid, String code) {
        if (uuid == null || code == null) {
            return false;
        }
        String redisKey = CAPTCHA_PREFIX + uuid;
        String cached = redisTemplate.opsForValue().get(redisKey);
        if (cached == null) {
            return false;
        }
        // 忽略大小写比较
        boolean ok = cached.equalsIgnoreCase(code);
        if (ok) {
            // 校验成功后删除验证码，防止重复使用
            redisTemplate.delete(redisKey);
        }
        return ok;
    }

    /**
     * 删除验证码（登录成功后清理）
     */
    public void remove(String uuid) {
        if (uuid != null) {
            redisTemplate.delete(CAPTCHA_PREFIX + uuid);
        }
    }
}
