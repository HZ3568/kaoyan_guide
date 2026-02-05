package com.example.controller;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.date.DateField;
import cn.hutool.core.date.DateTime;
import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.ObjectUtil;
import com.example.common.Result;
import com.example.common.enums.RoleEnum;
import com.example.entity.*;
import com.example.mapper.UniversitySpecialtysMapper;
import com.example.service.*;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

import java.util.*;

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
        } else if (RoleEnum.UNIVERSITY.name().equals(account.getRole())) {
            loginAccount = universityService.login(account);
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
        } else if (RoleEnum.UNIVERSITY.name().equals(account.getRole())) {
            University university = new University();
            BeanUtil.copyProperties(account, university);
            universityService.add(university);
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
        } else if (RoleEnum.UNIVERSITY.name().equals(account.getRole())) {
            universityService.updatePassword(account);
        }
        return Result.success();
    }

    @Resource
    private CategorysService categorysService;

    @Resource
    private SpecialtysService specialtysService;

    @Resource
    private ApplyService applyService;


    @GetMapping("/line")
    public Result line() {
        List<Apply> applyList = applyService.selectAll(null);
        Date today = new Date();
        DateTime start = DateUtil.offsetDay(today, -7);
        List<String> list = DateUtil.rangeToList(start, today, DateField.DAY_OF_YEAR).stream().map(DateUtil::formatDate).toList();
        Map<String, Object> result = new HashMap<>();
        result.put("x", list);
        List<Long> yList = new ArrayList<>();
        for (String day : list) {
            Long sum = applyList.stream().filter(x -> ObjectUtil.isNotEmpty(x.getTime()) && x.getTime().contains(day)).count();
            yList.add(sum);
        }
        result.put("y", yList);
        return Result.success(result);
    }

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

    @GetMapping("/bar")
    public Result bar() {
        List<Categorys> categorysList = categorysService.selectAll(null);
        List<Apply> applyList = applyService.selectAll(null);
        List<String> nameList = new ArrayList<>();
        List<Integer> totalList = new ArrayList<>();
        for (Categorys categorys : categorysList) {
            Integer sum = 0;
            for (Apply apply : applyList) {
                Specialtys specialtys1 = specialtysService.selectById(apply.getFirstSpecialtysId());
                if (specialtys1.getCategorysId() == categorys.getId()) {
                    sum ++;
                }
                Specialtys specialtys2 = specialtysService.selectById(apply.getSecondSpecialtysId());
                if (specialtys2.getCategorysId() == categorys.getId()) {
                    sum ++;
                }
                Specialtys specialtys3 = specialtysService.selectById(apply.getThirdSpecialtysId());
                if (specialtys3.getCategorysId() == categorys.getId()) {
                    sum ++;
                }
            }
            totalList.add(sum);
            nameList.add(categorys.getName());
        }

        HashMap<String, Object> map = new HashMap<>();
        map.put("nameList", nameList);
        map.put("totalList", totalList);
        return Result.success(map);
    }

    @GetMapping("/count")
    public Result count() {
        Map<String, Integer> map = new HashMap<>();
        List<Categorys> categorysList = categorysService.selectAll(null);
        map.put("categorysNumber", categorysList.size());

        List<Specialtys> specialtysList = specialtysService.selectAll(null);
        map.put("specialtysNumber", specialtysList.size());

        Long userNumber = userService.selectAll(null).stream().filter(x -> x.getStatus().equals("审核通过")).count();
        map.put("userNumber", userNumber.intValue());

        Long universityNumber = universityService.selectAll(null).stream().filter(x -> x.getStatus().equals("审核通过")).count();
        map.put("universityNumber", universityNumber.intValue());

        return Result.success(map);
    }

}
