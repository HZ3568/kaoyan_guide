package com.example.service;

import cn.hutool.core.util.ObjectUtil;
import com.example.common.enums.RoleEnum;
import com.example.entity.*;
import com.example.exception.CustomException;
import com.example.mapper.CategorysMapper;
import com.example.mapper.SpecialtysMapper;
import com.example.mapper.UniversityMapper;
import com.example.mapper.UniversitySpecialtysMapper;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * 学校专业业务处理
 **/
@Service
public class UniversitySpecialtysService {

    @Resource
    private UniversitySpecialtysMapper universitySpecialtysMapper;

    @Resource
    private UniversityMapper universityMapper;

    @Resource
    private CategorysMapper categorysMapper;

    @Resource
    private SpecialtysMapper specialtysMapper;

    /**
     * 新增
     */
    @Transactional
    public void add(UniversitySpecialtys universitySpecialtys) {
        Account currentUser = TokenUtils.getCurrentUser();
        universitySpecialtys.setUniversityId(currentUser.getId());
//        判断该学校是否已经加入该专业
        UniversitySpecialtys universitySpecialtys1 = universitySpecialtysMapper.selectByUniversityIdCategorysIdAndSpecialtysId(universitySpecialtys.getUniversityId(), universitySpecialtys.getCategorysId(), universitySpecialtys.getSpecialtysId());
        if (ObjectUtil.isNotEmpty(universitySpecialtys1)) {
            throw new CustomException("500", "该学校已有该门类的该专业，不可以重复添加");
        }
        universitySpecialtysMapper.insert(universitySpecialtys);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        universitySpecialtysMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            universitySpecialtysMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    @Transactional
    public void updateById(UniversitySpecialtys universitySpecialtys) {
//        判断修改前改学校是否已有该门类的该专业
        UniversitySpecialtys universitySpecialtys1 = universitySpecialtysMapper.selectByUniversityIdCategorysIdAndSpecialtysId(universitySpecialtys.getUniversityId(), universitySpecialtys.getCategorysId(), universitySpecialtys.getSpecialtysId());
        if (universitySpecialtys1.getId() != universitySpecialtys.getId()) {
            throw new CustomException("500", "该学校已有该门类的该专业，不可以重复添加");
        }
        universitySpecialtysMapper.updateById(universitySpecialtys);
    }

    /**
     * 根据ID查询
     */
    public UniversitySpecialtys selectById(Integer id) {
        UniversitySpecialtys universitySpecialtys = universitySpecialtysMapper.selectById(id);
        University university = universityMapper.selectById(universitySpecialtys.getUniversityId());
        if (ObjectUtil.isNotEmpty(university)) {
            universitySpecialtys.setUniversityName(university.getName());
        }
        Categorys categorys = categorysMapper.selectById(universitySpecialtys.getCategorysId());
        if (ObjectUtil.isNotEmpty(categorys)) {
            universitySpecialtys.setCategorysName(categorys.getName());
        }
        Specialtys specialtys = specialtysMapper.selectById(universitySpecialtys.getSpecialtysId());
        if (ObjectUtil.isNotEmpty(specialtys)) {
            universitySpecialtys.setSpecialtysName(specialtys.getName());
        }
        return universitySpecialtys;
    }

    /**
     * 查询所有
     */
    public List<UniversitySpecialtys> selectAll(UniversitySpecialtys universitySpecialtys) {
        return universitySpecialtysMapper.selectAll(universitySpecialtys);
    }

    /**
     * 分页查询
     */
    public PageInfo<UniversitySpecialtys> selectPage(UniversitySpecialtys universitySpecialtys, Integer pageNum, Integer pageSize) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (RoleEnum.UNIVERSITY.name().equals(currentUser.getRole())) {
            universitySpecialtys.setUniversityId(currentUser.getId());
        }
        PageHelper.startPage(pageNum, pageSize);
        List<UniversitySpecialtys> list = this.selectAll(universitySpecialtys);
        return PageInfo.of(list);
    }

}