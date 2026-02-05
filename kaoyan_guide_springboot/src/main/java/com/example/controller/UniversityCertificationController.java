package com.example.controller;

import com.example.common.Result;
import com.example.entity.UniversityCertification;
import com.example.service.UniversityCertificationService;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;
import jakarta.annotation.Resource;
import java.util.List;

/**
 * 大学认证信息前端操作接口
 **/
@RestController
@RequestMapping("/universityCertification")
public class UniversityCertificationController {

    @Resource
    private UniversityCertificationService universityCertificationService;

    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody UniversityCertification universityCertification) {
        universityCertificationService.add(universityCertification);
        return Result.success();
    }

    /**
     * 删除
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        universityCertificationService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     */
    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Integer> ids) {
        universityCertificationService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 修改
     */
    @PutMapping("/update")
    public Result updateById(@RequestBody UniversityCertification universityCertification) {
        universityCertificationService.updateById(universityCertification);
        return Result.success();
    }

    /**
     * 根据ID查询
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        UniversityCertification universityCertification = universityCertificationService.selectById(id);
        return Result.success(universityCertification);
    }

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(UniversityCertification universityCertification) {
        List<UniversityCertification> list = universityCertificationService.selectAll(universityCertification);
        return Result.success(list);
    }

    /**
     * 分页查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(UniversityCertification universityCertification,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<UniversityCertification> page = universityCertificationService.selectPage(universityCertification, pageNum, pageSize);
        return Result.success(page);
    }

    @GetMapping("/selectByUniversityId/{universityId}")
    public Result selectByUniversityId(@PathVariable Integer universityId) {
        UniversityCertification universityCertification = universityCertificationService.selectByUniversityId(universityId);
        return Result.success(universityCertification);
    }

}