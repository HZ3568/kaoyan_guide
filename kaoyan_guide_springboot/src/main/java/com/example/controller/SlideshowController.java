package com.example.controller;

import com.example.common.Result;
import com.example.entity.Slideshow;
import com.example.service.SlideshowService;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;
import jakarta.annotation.Resource;
import java.util.List;

/**
 * 轮播图信息前端操作接口
 **/
@RestController
@RequestMapping("/slideshow")
public class SlideshowController {

    @Resource
    private SlideshowService slideshowService;

    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody Slideshow slideshow) {
        slideshowService.add(slideshow);
        return Result.success();
    }

    /**
     * 删除
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        slideshowService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     */
    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Integer> ids) {
        slideshowService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 修改
     */
    @PutMapping("/update")
    public Result updateById(@RequestBody Slideshow slideshow) {
        slideshowService.updateById(slideshow);
        return Result.success();
    }

    /**
     * 根据ID查询
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        Slideshow slideshow = slideshowService.selectById(id);
        return Result.success(slideshow);
    }

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(Slideshow slideshow) {
        List<Slideshow> list = slideshowService.selectAll(slideshow);
        return Result.success(list);
    }

    /**
     * 分页查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(Slideshow slideshow,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<Slideshow> page = slideshowService.selectPage(slideshow, pageNum, pageSize);
        return Result.success(page);
    }

}