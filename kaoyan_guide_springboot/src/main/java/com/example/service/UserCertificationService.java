package com.example.service;

import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.ObjectUtil;
import com.example.entity.University;
import com.example.entity.User;
import com.example.entity.UserCertification;
import com.example.mapper.UserCertificationMapper;
import com.example.mapper.UserMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import java.util.List;

/**
 * 学生认证信息业务处理
 **/
@Service
public class UserCertificationService {

    @Resource
    private UserCertificationMapper userCertificationMapper;

    @Resource
    private UserMapper userMapper;

    /**
     * 新增
     */
    public void add(UserCertification userCertification) {
        userCertification.setStatus("待审核");
        userCertification.setTime(DateUtil.now());
        userCertificationMapper.insert(userCertification);

        User user = userMapper.selectById(userCertification.getUserId());
        if (ObjectUtil.isNotEmpty(user)) {
            user.setStatus("待审核");
            userMapper.updateById(user);
        }
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        userCertificationMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            userCertificationMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(UserCertification userCertification) {
        if (userCertification.getStatus().equals("审核通过")) {
            User user = userMapper.selectById(userCertification.getUserId());
            if (ObjectUtil.isNotEmpty(user)) {
                user.setStatus("审核通过");
                userMapper.updateById(user);
            }
        } else if (userCertification.getStatus().equals("待审核")) {
            User user = userMapper.selectById(userCertification.getUserId());
            if (ObjectUtil.isNotEmpty(user)) {
                user.setStatus("待审核");
                userMapper.updateById(user);
            }
        } else if (userCertification.getStatus().equals("审核拒绝")) {
            User user = userMapper.selectById(userCertification.getUserId());
            if (ObjectUtil.isNotEmpty(user)) {
                user.setStatus("审核拒绝");
                userMapper.updateById(user);
            }
        }
        userCertificationMapper.updateById(userCertification);
    }

    /**
     * 根据ID查询
     */
    public UserCertification selectById(Integer id) {
        return userCertificationMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<UserCertification> selectAll(UserCertification userCertification) {
        return userCertificationMapper.selectAll(userCertification);
    }

    /**
     * 分页查询
     */
    public PageInfo<UserCertification> selectPage(UserCertification userCertification, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<UserCertification> list = this.selectAll(userCertification);
        return PageInfo.of(list);
    }

    public UserCertification selectByUserId(Integer userId) {
        return userCertificationMapper.selectByUserId(userId);
    }
}