package com.example.service;

import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.ObjectUtil;
import com.example.common.enums.RoleEnum;
import com.example.entity.*;
import com.example.mapper.*;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 报考信息业务处理
 **/
@Service
public class ApplyService {

    @Resource
    private ApplyMapper applyMapper;

    @Resource
    private AreasMapper areasMapper;

    @Resource
    private UserCertificationMapper userCertificationMapper;

    @Resource
    private UniversityMapper universityMapper;

    @Resource
    private SpecialtysMapper specialtysMapper;

    /**
     * 新增
     */
    public void add(Apply apply) {
        Account currentUser = TokenUtils.getCurrentUser();
        apply.setUserId(currentUser.getId());
        apply.setFirstStatus("待录取");
        apply.setSecondStatus("待录取");
        apply.setThirdStatus("待录取");
        apply.setStatus("待录取");
        apply.setTime(DateUtil.now());
        applyMapper.insert(apply);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        applyMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            applyMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(Apply apply) {

        applyMapper.updateById(apply);
    }

    /**
     * 根据ID查询
     */
    public Apply selectById(Integer id) {
        return applyMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<Apply> selectAll(Apply apply) {
        return applyMapper.selectAll(apply);
    }

    /**
     * 分页查询
     */
    public PageInfo<Apply> selectPage(Apply apply, Integer pageNum, Integer pageSize) {
        Account currentUser = TokenUtils.getCurrentUser();
        if (RoleEnum.UNIVERSITY.name().equals(currentUser.getRole())) {
            apply.setFirstUniversityId(currentUser.getId());
            apply.setSecondUniversityId(currentUser.getId());
            apply.setThirdUniversityId(currentUser.getId());
        } else if (RoleEnum.USER.name().equals(currentUser.getRole())) {
            apply.setUserId(currentUser.getId());
        }
        PageHelper.startPage(pageNum, pageSize);
        List<Apply> list = this.selectAll(apply);
        for (Apply apply1 : list) {
            UserCertification userCertification = userCertificationMapper.selectByUserId(apply1.getUserId());
            if (ObjectUtil.isNotEmpty(userCertification)) {
                apply1.setScore(userCertification.getScore());
                apply1.setRanking(userCertification.getRanking());
                Areas areas = areasMapper.selectById(userCertification.getAreasId());
                if (ObjectUtil.isNotEmpty(areas)) {
                    apply1.setAreasName(areas.getName());
                }
            }
            University university = universityMapper.selectById(apply1.getFirstUniversityId());
            if (ObjectUtil.isNotEmpty(university)) {
                apply1.setFirstUniversityName(university.getName());
            }
            Specialtys specialtys = specialtysMapper.selectById(apply1.getFirstSpecialtysId());
            if (ObjectUtil.isNotEmpty(specialtys)) {
                apply1.setFirstSpecialtysName(specialtys.getName());
            }

            University university1 = universityMapper.selectById(apply1.getSecondUniversityId());
            if (ObjectUtil.isNotEmpty(university1)) {
                apply1.setSecondUniversityName(university1.getName());
            }
            Specialtys specialtys1 = specialtysMapper.selectById(apply1.getSecondSpecialtysId());
            if (ObjectUtil.isNotEmpty(specialtys1)) {
                apply1.setSecondSpecialtysName(specialtys1.getName());
            }

            University university2 = universityMapper.selectById(apply1.getThirdUniversityId());
            if (ObjectUtil.isNotEmpty(university2)) {
                apply1.setThirdUniversityName(university2.getName());
            }
            Specialtys specialtys2 = specialtysMapper.selectById(apply1.getThirdSpecialtysId());
            if (ObjectUtil.isNotEmpty(specialtys2)) {
                apply1.setThirdSpecialtysName(specialtys2.getName());
            }
        }
        return PageInfo.of(list);
    }

    public Apply selectByUserId(Integer id) {
        Apply apply = applyMapper.selectByUserId(id);
        return apply;
    }
}