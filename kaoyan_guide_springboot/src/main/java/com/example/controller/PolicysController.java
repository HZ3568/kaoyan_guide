package com.example.controller;

import com.example.common.Result;
import com.example.entity.Policys;
import com.example.service.PolicysService;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;
import jakarta.annotation.Resource;
import java.util.List;

/**
 * 招生政策前端操作接口
 **/
@RestController
@RequestMapping("/policys")
public class PolicysController {

    @Resource
    private PolicysService policysService;

    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody Policys policys) {
        policysService.add(policys);
        return Result.success();
    }

    /**
     * 删除
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        policysService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     */
    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Integer> ids) {
        policysService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 修改
     */
    @PutMapping("/update")
    public Result updateById(@RequestBody Policys policys) {
        policysService.updateById(policys);
        return Result.success();
    }

    /**
     * 根据ID查询
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        Policys policys = policysService.selectById(id);
        return Result.success(policys);
    }

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(Policys policys) {
        List<Policys> list = policysService.selectAll(policys);
        return Result.success(list);
    }

    /**
     * 分页查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(Policys policys,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<Policys> page = policysService.selectPage(policys, pageNum, pageSize);
        return Result.success(page);
    }

    @GetMapping("/loadHotPolicys")
    public Result loadHotPolicys() {
        List<Policys> list = policysService.loadHotPolicys();
        return Result.success(list);
    }

    /**
     * 更新浏览量
     */
    @GetMapping("/loadUpdateViewCount/{id}")
    public Result loadUpdateViewCount(@PathVariable Integer id) {
        policysService.loadUpdateViewCount(id);
        return Result.success();
    }

}