package com.example.controller;

import com.example.common.Result;
import com.example.entity.Areas;
import com.example.service.AreasService;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;
import jakarta.annotation.Resource;
import java.util.List;

/**
 * 地区信息前端操作接口
 **/
@RestController
@RequestMapping("/areas")
public class AreasController {

    @Resource
    private AreasService areasService;

    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody Areas areas) {
        areasService.add(areas);
        return Result.success();
    }

    /**
     * 删除
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        areasService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     */
    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Integer> ids) {
        areasService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 修改
     */
    @PutMapping("/update")
    public Result updateById(@RequestBody Areas areas) {
        areasService.updateById(areas);
        return Result.success();
    }

    /**
     * 根据ID查询
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        Areas areas = areasService.selectById(id);
        return Result.success(areas);
    }

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(Areas areas) {
        List<Areas> list = areasService.selectAll(areas);
        return Result.success(list);
    }

    /**
     * 分页查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(Areas areas,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<Areas> page = areasService.selectPage(areas, pageNum, pageSize);
        return Result.success(page);
    }

}