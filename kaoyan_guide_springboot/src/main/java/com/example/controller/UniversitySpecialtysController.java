package com.example.controller;

import com.example.common.Result;
import com.example.entity.UniversitySpecialtys;
import com.example.service.UniversitySpecialtysService;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;
import jakarta.annotation.Resource;
import java.util.List;

/**
 * 学校专业前端操作接口
 **/
@RestController
@RequestMapping("/universitySpecialtys")
public class UniversitySpecialtysController {

    @Resource
    private UniversitySpecialtysService universitySpecialtysService;

    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody UniversitySpecialtys universitySpecialtys) {
        universitySpecialtysService.add(universitySpecialtys);
        return Result.success();
    }

    /**
     * 删除
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        universitySpecialtysService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     */
    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Integer> ids) {
        universitySpecialtysService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 修改
     */
    @PutMapping("/update")
    public Result updateById(@RequestBody UniversitySpecialtys universitySpecialtys) {
        universitySpecialtysService.updateById(universitySpecialtys);
        return Result.success();
    }

    /**
     * 根据ID查询
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        UniversitySpecialtys universitySpecialtys = universitySpecialtysService.selectById(id);
        return Result.success(universitySpecialtys);
    }

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(UniversitySpecialtys universitySpecialtys) {
        List<UniversitySpecialtys> list = universitySpecialtysService.selectAll(universitySpecialtys);
        return Result.success(list);
    }

    /**
     * 分页查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(UniversitySpecialtys universitySpecialtys,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<UniversitySpecialtys> page = universitySpecialtysService.selectPage(universitySpecialtys, pageNum, pageSize);
        return Result.success(page);
    }

}