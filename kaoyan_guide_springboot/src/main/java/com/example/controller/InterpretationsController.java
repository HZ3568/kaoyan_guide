package com.example.controller;

import com.example.common.Result;
import com.example.entity.Interpretations;
import com.example.service.InterpretationsService;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;
import jakarta.annotation.Resource;
import java.util.List;

/**
 * 专业解读前端操作接口
 **/
@RestController
@RequestMapping("/interpretations")
public class InterpretationsController {

    @Resource
    private InterpretationsService interpretationsService;

    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody Interpretations interpretations) {
        interpretationsService.add(interpretations);
        return Result.success();
    }

    /**
     * 删除
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        interpretationsService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     */
    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Integer> ids) {
        interpretationsService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 修改
     */
    @PutMapping("/update")
    public Result updateById(@RequestBody Interpretations interpretations) {
        interpretationsService.updateById(interpretations);
        return Result.success();
    }

    /**
     * 根据ID查询
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        Interpretations interpretations = interpretationsService.selectById(id);
        return Result.success(interpretations);
    }

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(Interpretations interpretations) {
        List<Interpretations> list = interpretationsService.selectAll(interpretations);
        return Result.success(list);
    }

    /**
     * 分页查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(Interpretations interpretations,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<Interpretations> page = interpretationsService.selectPage(interpretations, pageNum, pageSize);
        return Result.success(page);
    }

    @GetMapping("/loadHotInterpretations")
    public Result loadHotInterpretations() {
        List<Interpretations> list = interpretationsService.loadHotInterpretations();
        return Result.success(list);
    }

    /**
     * 更新浏览量
     */
    @GetMapping("/loadUpdateViewCount/{id}")
    public Result loadUpdateViewCount(@PathVariable Integer id) {
        interpretationsService.loadUpdateViewCount(id);
        return Result.success();
    }

}