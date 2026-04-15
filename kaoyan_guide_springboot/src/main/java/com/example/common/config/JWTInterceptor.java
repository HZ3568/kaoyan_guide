package com.example.common.config;

import cn.hutool.core.util.ObjectUtil;
import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTVerifier;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.example.common.Constants;
import com.example.common.enums.ResultCodeEnum;
import com.example.common.enums.RoleEnum;
import com.example.entity.Account;
import com.example.exception.CustomException;
import com.example.service.AdminService;
import com.example.service.UserService;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * JWT 拦截器：校验 Token 有效性 + 路径角色一致性 + 固定密钥验签。
 *
 * 安全设计：
 * 1. Token 签发与验证均使用独立于用户密码的固定密钥，防止用户密码变更导致 Token 批量失效
 * 2. 路径级角色限制：/admin/** 路径仅允许 ADMIN 角色访问
 * 3. Token 解析后根据角色从对应服务查询用户，确保用户未被删除
 * 4. 验证码 Redis 存储防止暴力破解
 */
@Component
public class JWTInterceptor implements HandlerInterceptor {

    /** 管理员 Token 固定密钥 */
    private static final String ADMIN_SECRET = "KaoyanGuideAdminSecretKey2024";

    /** 用户 Token 固定密钥 */
    private static final String USER_SECRET = "KaoyanGuideUserSecretKey2024";

    @Resource
    private AdminService adminService;

    @Resource
    private UserService userService;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 1. 获取 Token
        String token = request.getHeader(Constants.TOKEN);
        if (ObjectUtil.isNull(token)) {
            token = request.getParameter(Constants.TOKEN);
        }
        if (token == null || token.trim().isEmpty()) {
            throw new CustomException(ResultCodeEnum.TOKEN_INVALID_ERROR.code, "未登录或登录已失效");
        }

        // 2. 解析 Token 获取角色
        String role;
        String userIdStr;
        try {
            String audience = JWT.decode(token).getAudience().get(0);
            String[] parts = audience.split("-");
            userIdStr = parts[0];
            role = parts[1];
        } catch (Exception e) {
            throw new CustomException(ResultCodeEnum.TOKEN_CHECK_ERROR.code, "Token 格式异常");
        }

        // 3. 根据角色查询用户，确保用户存在且未被删除
        Account account = null;
        if (RoleEnum.ADMIN.name().equals(role)) {
            account = adminService.selectById(Integer.valueOf(userIdStr));
        } else if (RoleEnum.USER.name().equals(role)) {
            account = userService.selectById(Integer.valueOf(userIdStr));
        }
        if (ObjectUtil.isNull(account)) {
            throw new CustomException(ResultCodeEnum.TOKEN_CHECK_ERROR.code, "用户不存在或已被删除");
        }

        // 4. 用固定密钥验签 Token（防止用旧密码密钥伪造 Token）
        String secret = RoleEnum.ADMIN.name().equals(role) ? ADMIN_SECRET : USER_SECRET;
        try {
            JWTVerifier jwtVerifier = JWT.require(Algorithm.HMAC256(secret)).build();
            jwtVerifier.verify(token);
        } catch (JWTVerificationException e) {
            throw new CustomException(ResultCodeEnum.TOKEN_CHECK_ERROR.code, "Token 校验失败，请重新登录");
        }

        // 5. 路径角色一致性校验：管理后台接口仅允许 ADMIN 角色访问
        String path = request.getRequestURI();
        if (path.startsWith("/admin") && !RoleEnum.ADMIN.name().equals(role)) {
            throw new CustomException("403", "无权限访问管理后台");
        }

        return true;
    }
}
