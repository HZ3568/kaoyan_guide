package com.example.controller;

import com.example.common.Result;
import com.example.entity.UserCertification;
import com.example.service.UserCertificationService;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;
import jakarta.annotation.Resource;
import java.util.List;

/**
 * 学生认证信息前端操作接口
 **/
@RestController
@RequestMapping("/userCertification")
public class UserCertificationController {

    @Resource
    private UserCertificationService userCertificationService;

    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody UserCertification userCertification) {
        userCertificationService.add(userCertification);
        return Result.success();
    }

    /**
     * 删除
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        userCertificationService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     */
    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Integer> ids) {
        userCertificationService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 修改
     */
    @PutMapping("/update")
    public Result updateById(@RequestBody UserCertification userCertification) {
        userCertificationService.updateById(userCertification);
        return Result.success();
    }

    /**
     * 根据ID查询
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        UserCertification userCertification = userCertificationService.selectById(id);
        return Result.success(userCertification);
    }

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(UserCertification userCertification) {
        List<UserCertification> list = userCertificationService.selectAll(userCertification);
        return Result.success(list);
    }

    /**
     * 分页查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(UserCertification userCertification,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<UserCertification> page = userCertificationService.selectPage(userCertification, pageNum, pageSize);
        return Result.success(page);
    }

    /**
     * 根据ID查询
     */
    @GetMapping("/selectByUserId/{userId}")
    public Result selectByUserId(@PathVariable Integer userId) {
        UserCertification userCertification = userCertificationService.selectByUserId(userId);
        return Result.success(userCertification);
    }

}