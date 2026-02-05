package com.example.service;

import com.example.entity.Areas;
import com.example.mapper.AreasMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import java.util.List;

/**
 * 地区信息业务处理
 **/
@Service
public class AreasService {

    @Resource
    private AreasMapper areasMapper;

    /**
     * 新增
     */
    public void add(Areas areas) {
        areasMapper.insert(areas);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        areasMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            areasMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(Areas areas) {
        areasMapper.updateById(areas);
    }

    /**
     * 根据ID查询
     */
    public Areas selectById(Integer id) {
        return areasMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<Areas> selectAll(Areas areas) {
        return areasMapper.selectAll(areas);
    }

    /**
     * 分页查询
     */
    public PageInfo<Areas> selectPage(Areas areas, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Areas> list = this.selectAll(areas);
        return PageInfo.of(list);
    }

}