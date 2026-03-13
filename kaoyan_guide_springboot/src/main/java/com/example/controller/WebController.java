package com.example.controller;

import cn.hutool.core.bean.BeanUtil;
import com.example.common.Result;
import com.example.common.enums.RoleEnum;
import com.example.entity.*;
import com.example.service.*;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class WebController {

    @Resource
    private AdminService adminService;

    @Resource
    private UserService userService;

    @Resource
    private UniversityService universityService;

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
