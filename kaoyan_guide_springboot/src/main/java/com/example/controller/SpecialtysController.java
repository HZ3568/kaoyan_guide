package com.example.controller;

import com.example.common.Result;
import com.example.entity.Specialtys;
import com.example.service.SpecialtysService;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;
import jakarta.annotation.Resource;
import java.util.List;

/**
 * 专业信息前端操作接口
 **/
@RestController
@RequestMapping("/specialtys")
public class SpecialtysController {

    @Resource
    private SpecialtysService specialtysService;

    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody Specialtys specialtys) {
        specialtysService.add(specialtys);
        return Result.success();
    }

    /**
     * 删除
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        specialtysService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     */
    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Integer> ids) {
        specialtysService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 修改
     */
    @PutMapping("/update")
    public Result updateById(@RequestBody Specialtys specialtys) {
        specialtysService.updateById(specialtys);
        return Result.success();
    }

    /**
     * 根据ID查询
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        Specialtys specialtys = specialtysService.selectById(id);
        return Result.success(specialtys);
    }

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(Specialtys specialtys) {
        List<Specialtys> list = specialtysService.selectAll(specialtys);
        return Result.success(list);
    }

    /**
     * 分页查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(Specialtys specialtys,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<Specialtys> page = specialtysService.selectPage(specialtys, pageNum, pageSize);
        return Result.success(page);
    }

}