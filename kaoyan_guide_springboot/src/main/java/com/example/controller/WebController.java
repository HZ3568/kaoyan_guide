package com.example.controller;

import cn.hutool.core.bean.BeanUtil;
import com.example.common.Result;
import com.example.common.enums.RoleEnum;
import com.example.entity.*;
import com.example.service.*;
import jakarta.annotation.Resource;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class WebController {

    private static final String CAPTCHA_PREFIX = "captcha:";
    private static final long CAPTCHA_EXPIRE_SECONDS = 60L;

    @Resource
    private AdminService adminService;

    @Resource
    private UserService userService;

    @Resource
    private UniversityService universityService;

    private final StringRedisTemplate redisTemplate;

    public WebController(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    /**
     * 默认请求接口
     */
    @GetMapping("/")
    public Result hello () {
        return Result.success();
    }

    /**
     * 登录
     */
    @PostMapping("/login")
    public Result login(@RequestBody Account account) {
        // 验证码校验
        String uuid = account.getUuid();
        String captcha = account.getCaptcha();
        if (uuid == null || captcha == null || captcha.trim().isEmpty()) {
            return Result.error("400", "请输入验证码");
        }
        String redisKey = CAPTCHA_PREFIX + uuid;
        String cached = redisTemplate.opsForValue().get(redisKey);
        if (cached == null) {
            return Result.error("400", "验证码已过期，请重新获取");
        }
        if (!cached.equalsIgnoreCase(captcha.trim())) {
            return Result.error("400", "验证码错误");
        }
        // 校验成功，删除 Redis 中的验证码
        redisTemplate.delete(redisKey);

        // 正常登录
        Account loginAccount = null;
        if (RoleEnum.ADMIN.name().equals(account.getRole())) {
            loginAccount = adminService.login(account);
        } else if (RoleEnum.USER.name().equals(account.getRole())) {
            loginAccount = userService.login(account);
        }
        return Result.success(loginAccount);
    }

    /**
     * 注册
     */
    @PostMapping("/register")
    public Result register(@RequestBody Account account)  {
        if (RoleEnum.USER.name().equals(account.getRole())) {
            User user = new User();
            BeanUtil.copyProperties(account, user);
            // 不设置头像，让前端显示本地默认头像
            user.setAvatar(null);
            userService.add(user);
        }
        return Result.success();
    }

    /**
     * 修改密码
     */
    @PutMapping("/updatePassword")
    public Result updatePassword(@RequestBody Account account) {
        if (RoleEnum.ADMIN.name().equals(account.getRole())) {
            adminService.updatePassword(account);
        } else if (RoleEnum.USER.name().equals(account.getRole())) {
            userService.updatePassword(account);
        }
        return Result.success();
    }

    @Resource
    private CategorysService categorysService;

    @Resource
    private SpecialtysService specialtysService;


    @GetMapping("/pie")
    public Result pie() {
        List<Categorys> categorysList = categorysService.selectAll(null);
        List<Specialtys> specialtysList = specialtysService.selectAll(null);
        List<Map<String, Object>> list = new ArrayList<>();
        Map<String, Object> map;
        for (Categorys categorys : categorysList) {
            map = new HashMap<>();
            map.put("name", categorys.getName());
            map.put("value", specialtysList.stream().filter(p -> p.getCategorysId().equals(categorys.getId())).count());
            list.add(map);
        }
        return Result.success(list);
    }

    @GetMapping("/count")
    public Result count() {
        Map<String, Integer> map = new HashMap<>();
        List<Categorys> categorysList = categorysService.selectAll(null);
        map.put("categorysNumber", categorysList.size());

        List<Specialtys> specialtysList = specialtysService.selectAll(null);
        map.put("specialtysNumber", specialtysList.size());

        map.put("userNumber", userService.selectAll(null).size());
        map.put("universityNumber", universityService.selectAll(null).size());

        return Result.success(map);
    }

}
