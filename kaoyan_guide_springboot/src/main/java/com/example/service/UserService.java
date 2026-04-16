package com.example.service;

import cn.hutool.core.util.ObjectUtil;
import com.example.common.Constants;
import com.example.common.enums.ResultCodeEnum;
import com.example.common.enums.RoleEnum;
import com.example.common.enums.StatusEnum;
import com.example.entity.Account;
import com.example.entity.User;
import com.example.exception.CustomException;
import com.example.mapper.UserMapper;
import com.example.utils.PasswordEncoder;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.regex.Pattern;

/**
 * 用户业务层
 */
@Service
public class UserService {

    /** 固定 Token 签名密钥（独立于用户密码） */
    private static final String TOKEN_SECRET = "KaoyanGuideUserSecretKey2024";

    /** 登录密码：6-20位字母或数字 */
    private static final Pattern PASSWORD_PATTERN = Pattern.compile("^[a-zA-Z0-9]{6,20}$");

    /** 手机号：11位纯数字 */
    private static final Pattern PHONE_PATTERN = Pattern.compile("^\\d{11}$");

    /** 邮箱：标准格式 */
    private static final Pattern EMAIL_PATTERN = Pattern.compile("^[\\w.-]+@[\\w.-]+\\.\\w+$");

    @Resource
    private UserMapper userMapper;

    /**
     * 新增用户（注册）
     */
    public void add(User user) {
        validateForAdd(user);
        User dbUser = userMapper.selectByUsername(user.getUsername());
        if (ObjectUtil.isNotNull(dbUser)) {
            throw new CustomException(ResultCodeEnum.USER_EXIST_ERROR);
        }
        // 密码为空时使用默认密码并加密存储
        if (ObjectUtil.isEmpty(user.getPassword())) {
            user.setPassword(Constants.USER_DEFAULT_PASSWORD);
        }
        user.setPassword(PasswordEncoder.encode(user.getPassword()));
        if (ObjectUtil.isEmpty(user.getName())) {
            user.setName(user.getUsername());
        }
        user.setRole(RoleEnum.USER.name());
        user.setStatus(StatusEnum.NORMAL.code());
        userMapper.insert(user);
    }

    /**
     * 更新用户信息（不含密码）
     */
    public void updateById(User user) {
        validateForUpdate(user);
        userMapper.updateById(user);
    }

    /**
     * 修改密码（需校验旧密码后用 BCrypt 存储新密码）
     */
    public void updatePassword(Account account) {
        if (ObjectUtil.isEmpty(account.getUsername()) || ObjectUtil.isEmpty(account.getPassword())
                || ObjectUtil.isEmpty(account.getNewPassword())) {
            throw new CustomException(ResultCodeEnum.PARAM_ERROR);
        }
        if (!PASSWORD_PATTERN.matcher(account.getNewPassword()).matches()) {
            throw new CustomException("400", "新密码必须为6-20位字母或数字");
        }
        User dbUser = userMapper.selectByUsername(account.getUsername());
        if (ObjectUtil.isNull(dbUser)) {
            throw new CustomException(ResultCodeEnum.USER_NOT_EXIST_ERROR);
        }
        if (!PasswordEncoder.matches(account.getPassword(), dbUser.getPassword())) {
            throw new CustomException(ResultCodeEnum.PARAM_PASSWORD_ERROR);
        }
        dbUser.setPassword(PasswordEncoder.encode(account.getNewPassword()));
        userMapper.updateById(dbUser);
    }

    public void deleteById(Integer id) {
        userMapper.deleteById(id);
    }

    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            userMapper.deleteById(id);
        }
    }

    public User selectById(Integer id) {
        return userMapper.selectById(id);
    }

    public List<User> selectAll(User user) {
        return userMapper.selectAll(user);
    }

    public PageInfo<User> selectPage(User user, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<User> list = userMapper.selectAll(user);
        return PageInfo.of(list);
    }

    /**
     * 用户登录（BCrypt 校验 + 固定密钥签发 Token）
     */
    public User login(Account account) {
        User dbUser = userMapper.selectByUsername(account.getUsername());
        if (ObjectUtil.isNull(dbUser)) {
            throw new CustomException(ResultCodeEnum.USER_NOT_EXIST_ERROR);
        }
        if (!PasswordEncoder.matches(account.getPassword(), dbUser.getPassword())) {
            throw new CustomException(ResultCodeEnum.USER_ACCOUNT_ERROR);
        }
        // 校验账号状态：只有正常状态(1)才允许登录
        if (dbUser.getStatus() == null || !StatusEnum.NORMAL.code().equals(dbUser.getStatus())) {
            throw new CustomException("401", "账号已被禁用，无法登录");
        }
        // 使用固定密钥签发 Token，避免用户修改密码导致所有 Token 失效
        String token = TokenUtils.createToken(dbUser.getId() + "-" + dbUser.getRole(), TOKEN_SECRET);
        dbUser.setToken(token);
        return dbUser;
    }

    /**
     * 新增时字段格式校验
     */
    private void validateForAdd(User user) {
        if (ObjectUtil.isEmpty(user.getUsername())) {
            throw new CustomException("400", "账号不能为空");
        }
        if (user.getUsername().length() < 3 || user.getUsername().length() > 20) {
            throw new CustomException("400", "账号长度需在3-20位之间");
        }
        if (ObjectUtil.isNotNull(user.getPhone()) && !PHONE_PATTERN.matcher(user.getPhone()).matches()) {
            throw new CustomException("400", "手机号必须为11位数字");
        }
        if (ObjectUtil.isNotNull(user.getEmail()) && !EMAIL_PATTERN.matcher(user.getEmail()).matches()) {
            throw new CustomException("400", "邮箱格式不正确");
        }
    }

    /**
     * 更新时字段格式校验（仅当字段非空时才校验）
     */
    private void validateForUpdate(User user) {
        if (ObjectUtil.isNotNull(user.getPhone()) && !PHONE_PATTERN.matcher(user.getPhone()).matches()) {
            throw new CustomException("400", "手机号必须为11位数字");
        }
        if (ObjectUtil.isNotNull(user.getEmail()) && !EMAIL_PATTERN.matcher(user.getEmail()).matches()) {
            throw new CustomException("400", "邮箱格式不正确");
        }
    }
}
