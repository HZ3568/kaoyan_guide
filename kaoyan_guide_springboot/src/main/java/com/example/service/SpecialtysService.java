package com.example.service;

import com.example.entity.Specialtys;
import com.example.mapper.SpecialtysMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import java.util.List;

/**
 * 专业信息业务处理
 **/
@Service
public class SpecialtysService {

    @Resource
    private SpecialtysMapper specialtysMapper;

    /**
     * 新增
     */
    public void add(Specialtys specialtys) {
        specialtysMapper.insert(specialtys);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        specialtysMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            specialtysMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(Specialtys specialtys) {
        specialtysMapper.updateById(specialtys);
    }

    /**
     * 根据ID查询
     */
    public Specialtys selectById(Integer id) {
        return specialtysMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<Specialtys> selectAll(Specialtys specialtys) {
        return specialtysMapper.selectAll(specialtys);
    }

    /**
     * 分页查询
     */
    public PageInfo<Specialtys> selectPage(Specialtys specialtys, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Specialtys> list = this.selectAll(specialtys);
        return PageInfo.of(list);
    }

}