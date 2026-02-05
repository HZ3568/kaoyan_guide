package com.example.service;

import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.ObjectUtil;
import com.example.entity.University;
import com.example.entity.UniversityCertification;
import com.example.mapper.UniversityCertificationMapper;
import com.example.mapper.UniversityMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import java.util.List;

/**
 * 大学认证信息业务处理
 **/
@Service
public class UniversityCertificationService {

    @Resource
    private UniversityCertificationMapper universityCertificationMapper;

    @Resource
    private UniversityMapper universityMapper;

    /**
     * 新增
     */
    public void add(UniversityCertification universityCertification) {
        universityCertification.setTime(DateUtil.now());
        universityCertification.setStatus("待审核");
        universityCertificationMapper.insert(universityCertification);

        University university = universityMapper.selectById(universityCertification.getUniversityId());
        if (ObjectUtil.isNotEmpty(university)) {
            university.setStatus("待审核");
            universityMapper.updateById(university);
        }
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        universityCertificationMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            universityCertificationMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(UniversityCertification universityCertification) {
        if (universityCertification.getStatus().equals("审核通过")) {
            University university = universityMapper.selectById(universityCertification.getUniversityId());
            if (ObjectUtil.isNotEmpty(university)) {
                university.setStatus("审核通过");
                universityMapper.updateById(university);
            }
        } else if (universityCertification.getStatus().equals("待审核")) {
            University university = universityMapper.selectById(universityCertification.getUniversityId());
            if (ObjectUtil.isNotEmpty(university)) {
                university.setStatus("待审核");
                universityMapper.updateById(university);
            }
        } else if (universityCertification.getStatus().equals("审核拒绝")) {
            University university = universityMapper.selectById(universityCertification.getUniversityId());
            if (ObjectUtil.isNotEmpty(university)) {
                university.setStatus("审核拒绝");
                universityMapper.updateById(university);
            }
        }
        universityCertificationMapper.updateById(universityCertification);
    }

    /**
     * 根据ID查询
     */
    public UniversityCertification selectById(Integer id) {
        return universityCertificationMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<UniversityCertification> selectAll(UniversityCertification universityCertification) {
        return universityCertificationMapper.selectAll(universityCertification);
    }

    /**
     * 分页查询
     */
    public PageInfo<UniversityCertification> selectPage(UniversityCertification universityCertification, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<UniversityCertification> list = this.selectAll(universityCertification);
        return PageInfo.of(list);
    }

    public UniversityCertification selectByUniversityId(Integer universityId) {
        return universityCertificationMapper.selectByUniversityId(universityId);
    }
}