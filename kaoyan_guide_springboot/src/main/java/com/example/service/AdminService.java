package com.example.service;

import cn.hutool.core.util.ObjectUtil;
import com.example.common.Constants;
import com.example.common.enums.ResultCodeEnum;
import com.example.common.enums.RoleEnum;
import com.example.common.enums.StatusEnum;
import com.example.entity.Account;
import com.example.entity.Admin;
import com.example.exception.CustomException;
import com.example.mapper.AdminMapper;
import com.example.utils.PasswordEncoder;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.regex.Pattern;

/**
 * 管理员业务层
 */
@Service
public class AdminService {

    /** 固定 Token 签名密钥（独立于用户密码） */
    private static final String TOKEN_SECRET = "KaoyanGuideAdminSecretKey2024";

    /** 登录密码：6-20位，至少一个字母+一个数字，允许其他符号 */
    private static final Pattern PASSWORD_PATTERN = Pattern.compile("^(?=.*[a-zA-Z])(?=.*\\d).{6,20}$");

    /** 手机号：11位纯数字 */
    private static final Pattern PHONE_PATTERN = Pattern.compile("^\\d{11}$");

    /** 邮箱：标准格式 */
    private static final Pattern EMAIL_PATTERN = Pattern.compile("^[\\w.-]+@[\\w.-]+\\.\\w+$");

    @Resource
    private AdminMapper adminMapper;

    /**
     * 新增管理员
     */
    public void add(Admin admin) {
        validateForAdd(admin);
        Admin dbAdmin = adminMapper.selectByUsername(admin.getUsername());
        if (ObjectUtil.isNotNull(dbAdmin)) {
            throw new CustomException(ResultCodeEnum.USER_EXIST_ERROR);
        }
        // 密码为空时使用默认密码并加密存储
        if (ObjectUtil.isEmpty(admin.getPassword())) {
            admin.setPassword(Constants.USER_DEFAULT_PASSWORD);
        }
        admin.setPassword(PasswordEncoder.encode(admin.getPassword()));
        if (ObjectUtil.isEmpty(admin.getName())) {
            admin.setName(admin.getUsername());
        }
        admin.setRole(RoleEnum.ADMIN.name());
        admin.setStatus(1);
        adminMapper.insert(admin);
    }

    /**
     * 更新管理员信息（不含密码）
     */
    public void updateById(Admin admin) {
        validateForUpdate(admin);
        adminMapper.updateById(admin);
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
            throw new CustomException("400", "新密码必须为6-20位且同时包含字母和数字");
        }
        Admin dbAdmin = adminMapper.selectByUsername(account.getUsername());
        if (ObjectUtil.isNull(dbAdmin)) {
            throw new CustomException(ResultCodeEnum.USER_NOT_EXIST_ERROR);
        }
        if (!PasswordEncoder.matches(account.getPassword(), dbAdmin.getPassword())) {
            throw new CustomException(ResultCodeEnum.PARAM_PASSWORD_ERROR);
        }
        dbAdmin.setPassword(PasswordEncoder.encode(account.getNewPassword()));
        adminMapper.updateById(dbAdmin);
    }

    public void deleteById(Integer id) {
        adminMapper.deleteById(id);
    }

    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            adminMapper.deleteById(id);
        }
    }

    public Admin selectById(Integer id) {
        return adminMapper.selectById(id);
    }

    public List<Admin> selectAll(Admin admin) {
        return adminMapper.selectAll(admin);
    }

    public PageInfo<Admin> selectPage(Admin admin, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Admin> list = adminMapper.selectAll(admin);
        return PageInfo.of(list);
    }

    /**
     * 管理员登录（BCrypt 校验 + 固定密钥签发 Token）
     */
    public Admin login(Account account) {
        System.out.println("[AdminService.login] ====== 管理员登录开始 ======");
        System.out.println("[AdminService.login] 输入: username=" + account.getUsername() + ", role=" + account.getRole() + ", password存在=" + (account.getPassword() != null));

        Admin dbAdmin = adminMapper.selectByUsername(account.getUsername());
        System.out.println("[AdminService.login] 查表结果: " + (dbAdmin != null ? "找到 admin, id=" + dbAdmin.getId() + ", username=" + dbAdmin.getUsername() + ", status=" + dbAdmin.getStatus() + ", password有值=" + (dbAdmin.getPassword() != null) : "null(未找到)"));

        if (ObjectUtil.isNull(dbAdmin)) {
            System.out.println("[AdminService.login] 管理员不存在，抛出异常");
            throw new CustomException(ResultCodeEnum.USER_NOT_EXIST_ERROR.code, "账号不存在");
        }

        boolean passwordMatch = PasswordEncoder.matches(account.getPassword(), dbAdmin.getPassword());
        System.out.println("[AdminService.login] 密码校验: " + passwordMatch + " (输入密码=" + account.getPassword() + ")");

        if (!passwordMatch) {
            System.out.println("[AdminService.login] 密码错误，抛出异常");
            throw new CustomException(ResultCodeEnum.USER_ACCOUNT_ERROR.code, "密码错误");
        }

        System.out.println("[AdminService.login] status检查: dbAdmin.status=" + dbAdmin.getStatus() + ", NORMAL.code()=" + StatusEnum.NORMAL.code());
        // 校验账号状态：只有正常状态(1)才允许登录
        if (dbAdmin.getStatus() == null || !StatusEnum.NORMAL.code().equals(dbAdmin.getStatus())) {
            System.out.println("[AdminService.login] 账号已被禁用，status=" + dbAdmin.getStatus() + "，抛出异常");
            throw new CustomException("401", "账号已被禁用，无法登录");
        }
        System.out.println("[AdminService.login] status检查通过，可以登录");

        // 使用固定密钥签发 Token，避免用户修改密码导致所有 Token 失效
        String tokenStr = dbAdmin.getId() + "-" + dbAdmin.getRole();
        System.out.println("[AdminService.login] 生成token, audience=" + tokenStr + ", secret=" + TOKEN_SECRET);
        String token = TokenUtils.createToken(tokenStr, TOKEN_SECRET);
        System.out.println("[AdminService.login] token生成结果: " + (token != null ? "成功(" + token.substring(0, Math.min(20, token.length())) + "...)" : "null"));

        dbAdmin.setToken(token);
        System.out.println("[AdminService.login] setToken完成, dbAdmin.token=" + (dbAdmin.getToken() != null ? "有值" : "null"));
        System.out.println("[AdminService.login] ====== 管理员登录成功 ======");
        return dbAdmin;
    }

    /**
     * 新增时字段格式校验
     */
    private void validateForAdd(Admin admin) {
        if (ObjectUtil.isEmpty(admin.getUsername())) {
            throw new CustomException("400", "账号不能为空");
        }
        if (admin.getUsername().length() < 3 || admin.getUsername().length() > 20) {
            throw new CustomException("400", "账号长度需在3-20位之间");
        }
        if (ObjectUtil.isNotNull(admin.getPhone()) && !PHONE_PATTERN.matcher(admin.getPhone()).matches()) {
            throw new CustomException("400", "手机号必须为11位数字");
        }
        if (ObjectUtil.isNotNull(admin.getEmail()) && !EMAIL_PATTERN.matcher(admin.getEmail()).matches()) {
            throw new CustomException("400", "邮箱格式不正确");
        }
    }

    /**
     * 更新时字段格式校验（仅当字段非空时才校验）
     */
    private void validateForUpdate(Admin admin) {
        if (ObjectUtil.isNotNull(admin.getPhone()) && !PHONE_PATTERN.matcher(admin.getPhone()).matches()) {
            throw new CustomException("400", "手机号必须为11位数字");
        }
        if (ObjectUtil.isNotNull(admin.getEmail()) && !EMAIL_PATTERN.matcher(admin.getEmail()).matches()) {
            throw new CustomException("400", "邮箱格式不正确");
        }
    }
}
