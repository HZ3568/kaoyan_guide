package com.example.service;

import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.ObjectUtil;
import com.example.entity.Categorys;
import com.example.entity.Interpretations;
import com.example.mapper.CategorysMapper;
import com.example.mapper.InterpretationsMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import org.springframework.util.ObjectUtils;

import java.util.List;

/**
 * 专业解读业务处理
 **/
@Service
public class InterpretationsService {

    @Resource
    private InterpretationsMapper interpretationsMapper;

    @Resource
    private CategorysMapper categorysMapper;

    /**
     * 新增
     */
    public void add(Interpretations interpretations) {
        interpretations.setTime(DateUtil.now());
        interpretations.setViewCount(0);
        interpretationsMapper.insert(interpretations);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        interpretationsMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            interpretationsMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(Interpretations interpretations) {
        interpretationsMapper.updateById(interpretations);
    }

    /**
     * 根据ID查询
     */
    public Interpretations selectById(Integer id) {
        Interpretations interpretations = interpretationsMapper.selectById(id);
        Categorys categorys = categorysMapper.selectById(interpretations.getCategorysId());
        if (ObjectUtil.isNotEmpty(categorys)) {
            interpretations.setCategorysName(categorys.getName());
        }
        return interpretations;
    }

    /**
     * 查询所有
     */
    public List<Interpretations> selectAll(Interpretations interpretations) {
        return interpretationsMapper.selectAll(interpretations);
    }

    /**
     * 分页查询
     */
    public PageInfo<Interpretations> selectPage(Interpretations interpretations, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Interpretations> list = this.selectAll(interpretations);
        return PageInfo.of(list);
    }

    public List<Interpretations> loadHotInterpretations() {
        return interpretationsMapper.loadHotInterpretations();
    }

    public void loadUpdateViewCount(Integer id) {
        Interpretations interpretations = interpretationsMapper.selectById(id);
        interpretations.setViewCount(interpretations.getViewCount() + 1);
        interpretationsMapper.updateById(interpretations);
    }
}