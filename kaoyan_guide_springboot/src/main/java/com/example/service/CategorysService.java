package com.example.service;

import com.example.entity.Categorys;
import com.example.mapper.CategorysMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import java.util.List;

/**
 * 门类信息业务处理
 **/
@Service
public class CategorysService {

    @Resource
    private CategorysMapper categorysMapper;

    /**
     * 新增
     */
    public void add(Categorys categorys) {
        categorysMapper.insert(categorys);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        categorysMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            categorysMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(Categorys categorys) {
        categorysMapper.updateById(categorys);
    }

    /**
     * 根据ID查询
     */
    public Categorys selectById(Integer id) {
        return categorysMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<Categorys> selectAll(Categorys categorys) {
        return categorysMapper.selectAll(categorys);
    }

    /**
     * 分页查询
     */
    public PageInfo<Categorys> selectPage(Categorys categorys, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Categorys> list = this.selectAll(categorys);
        return PageInfo.of(list);
    }

}