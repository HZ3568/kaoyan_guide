package com.example.controller;

import com.example.common.Result;
import com.example.entity.University;
import com.example.service.UniversityService;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 前端请求接口
 */
@RestController
@RequestMapping("/university")
public class UniversityController {

    @Resource
    private UniversityService universityService;

    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody University university) {
        universityService.add(university);
        return Result.success();
    }

    /**
     * 修改
     */
    @PutMapping("/update")
    public Result update(@RequestBody University university) {
        universityService.updateById(university);
        return Result.success();
    }

    /**
     * 单个删除
     */
    @DeleteMapping("/delete/{id}")
    public Result delete(@PathVariable Integer id) {
        universityService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     */
    @DeleteMapping("/delete/batch")
    public Result delete(@RequestBody List<Integer> ids) {
        universityService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 单个查询
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        University university = universityService.selectById(id);
        return Result.success(university);
    }

    /**
     * 单个查询
     */
    @GetMapping("/selectByUniversityId/{id}")
    public Result selectByUniversityId(@PathVariable Integer id) {
        University university = universityService.selectByUniversityId(id);
        return Result.success(university);
    }

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(University university) {
        List<University> list = universityService.selectAll(university);
        return Result.success(list);
    }

    /**
     * 分页查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(University university,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<University> pageInfo = universityService.selectPage(university, pageNum, pageSize);
        return Result.success(pageInfo);
    }


    @GetMapping("/loadHotUniversity")
    public Result loadHotUniversity() {
        List<University> list = universityService.loadHotUniversity();
        return Result.success(list);
    }
}
