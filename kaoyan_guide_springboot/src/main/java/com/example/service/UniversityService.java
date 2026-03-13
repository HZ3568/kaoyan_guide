package com.example.service;

import cn.hutool.core.util.ObjectUtil;
import com.example.common.Constants;
import com.example.common.enums.ResultCodeEnum;
import com.example.common.enums.RoleEnum;
import com.example.entity.*;
import com.example.exception.CustomException;
import com.example.mapper.AreasMapper;
import com.example.mapper.CollectMapper;
import com.example.mapper.CommentMapper;
import com.example.mapper.UniversityMapper;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 业务层方法
 */
@Service
public class UniversityService {

    @Resource
    private UniversityMapper universityMapper;

    @Resource
    private AreasMapper areasMapper;

    @Resource
    private CollectMapper collectMapper;

    @Resource
    private CommentMapper commentMapper;


    public void add(University university) {
        University dbUniversity = universityMapper.selectByUsername(university.getUsername());
        if (ObjectUtil.isNotNull(dbUniversity)) {
            throw new CustomException(ResultCodeEnum.USER_EXIST_ERROR);
        }
        if (ObjectUtil.isEmpty(university.getPassword())) {
            university.setPassword(Constants.USER_DEFAULT_PASSWORD);
        }
        if (ObjectUtil.isEmpty(university.getName())) {
            university.setName(university.getUsername());
        }
        university.setStatus("待认证");
        university.setRole(RoleEnum.USER.name());
        universityMapper.insert(university);
    }

    public void updateById(University university) {
        universityMapper.updateById(university);
    }

    public void deleteById(Integer id) {
        universityMapper.deleteById(id);
    }

    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            universityMapper.deleteById(id);
        }
    }

    public University selectById(Integer id) {
        return universityMapper.selectById(id);
    }

    public University selectByUniversityId(Integer id) {
        Account currentUser = TokenUtils.getCurrentUser();
        University university = universityMapper.selectById(id);
        Areas areas = areasMapper.selectById(university.getAreasId());
        if (ObjectUtil.isNotEmpty(areas)) {
            university.setAreasName(areas.getName());
        }
        Collect collect = collectMapper.selectByUniversityIdAndUserId(university.getId(), currentUser.getId());
        if (ObjectUtil.isNotEmpty(collect)) {
            university.setCollectFlag(true);
        } else {
            university.setCollectFlag(false);
        }

        Comment comment = commentMapper.selectByUserIdAndUniversityId(currentUser.getId(), id);
        if (ObjectUtil.isNotEmpty(comment)) {
            university.setCommentFlag(true);
        } else {
            university.setCommentFlag(false);
        }

        return university;
    }

    public List<University> selectAll(University university) {
        return universityMapper.selectAll(university);
    }

    public PageInfo<University> selectPage(University university, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<University> list = universityMapper.selectAll(university);
        return PageInfo.of(list);
    }

    /**
     * 登录
     */
    public University login(Account account) {
        University dbUniversity = universityMapper.selectByUsername(account.getUsername());
        if (ObjectUtil.isNull(dbUniversity)) {
            throw new CustomException(ResultCodeEnum.USER_NOT_EXIST_ERROR);
        }
        if (!dbUniversity.getPassword().equals(account.getPassword())) {
            throw new CustomException(ResultCodeEnum.USER_ACCOUNT_ERROR);
        }
        // 生成token
        String token = TokenUtils.createToken(dbUniversity.getId() + "-" + dbUniversity.getRole(), dbUniversity.getPassword());
        dbUniversity.setToken(token);
        return dbUniversity;
    }

    /**
     * 修改密码
     */
    public void updatePassword(Account account) {
        University dbUniversity = universityMapper.selectByUsername(account.getUsername());
        if (ObjectUtil.isNull(dbUniversity)) {
            throw new CustomException(ResultCodeEnum.USER_NOT_EXIST_ERROR);
        }
        if (!account.getPassword().equals(dbUniversity.getPassword())) {
            throw new CustomException(ResultCodeEnum.PARAM_PASSWORD_ERROR);
        }
        dbUniversity.setPassword(account.getNewPassword());
        universityMapper.updateById(dbUniversity);
    }

    public List<University> loadHotUniversity() {
        return universityMapper.loadHotUniversity();
    }
}
