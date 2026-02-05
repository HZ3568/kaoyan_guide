package com.example.controller;

import com.example.common.Result;
import com.example.entity.Categorys;
import com.example.service.CategorysService;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;
import jakarta.annotation.Resource;
import java.util.List;

/**
 * 门类信息前端操作接口
 **/
@RestController
@RequestMapping("/categorys")
public class CategorysController {

    @Resource
    private CategorysService categorysService;

    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody Categorys categorys) {
        categorysService.add(categorys);
        return Result.success();
    }

    /**
     * 删除
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        categorysService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     */
    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Integer> ids) {
        categorysService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 修改
     */
    @PutMapping("/update")
    public Result updateById(@RequestBody Categorys categorys) {
        categorysService.updateById(categorys);
        return Result.success();
    }

    /**
     * 根据ID查询
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        Categorys categorys = categorysService.selectById(id);
        return Result.success(categorys);
    }

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(Categorys categorys) {
        List<Categorys> list = categorysService.selectAll(categorys);
        return Result.success(list);
    }

    /**
     * 分页查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(Categorys categorys,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<Categorys> page = categorysService.selectPage(categorys, pageNum, pageSize);
        return Result.success(page);
    }

}