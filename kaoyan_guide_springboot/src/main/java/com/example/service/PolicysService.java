package com.example.service;

import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.ObjectUtil;
import com.example.entity.Account;
import com.example.entity.Policys;
import com.example.entity.University;
import com.example.mapper.PolicysMapper;
import com.example.mapper.UniversityMapper;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import java.util.List;

/**
 * 招生政策业务处理
 **/
@Service
public class PolicysService {

    @Resource
    private PolicysMapper policysMapper;

    @Resource
    private UniversityMapper universityMapper;

    /**
     * 新增
     */
    public void add(Policys policys) {
        Account currentUser = TokenUtils.getCurrentUser();
        policys.setUniversityId(currentUser.getId());
        policys.setTime(DateUtil.now());
        policys.setViewCount(0);
        policysMapper.insert(policys);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        policysMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            policysMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(Policys policys) {
        policysMapper.updateById(policys);
    }

    /**
     * 根据ID查询
     */
    public Policys selectById(Integer id) {
        Policys policys = policysMapper.selectById(id);
        University university = universityMapper.selectById(policys.getUniversityId());
        if (ObjectUtil.isNotEmpty(university)) {
            policys.setUniversityName(university.getName());
        }
        return policys;
    }

    /**
     * 查询所有
     */
    public List<Policys> selectAll(Policys policys) {
        return policysMapper.selectAll(policys);
    }

    /**
     * 分页查询
     */
    public PageInfo<Policys> selectPage(Policys policys, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Policys> list = this.selectAll(policys);
        return PageInfo.of(list);
    }

    public List<Policys> loadHotPolicys() {
        return policysMapper.loadHotPolicys();
    }

    public void loadUpdateViewCount(Integer id) {
        Policys policys = policysMapper.selectById(id);
        policys.setViewCount(policys.getViewCount() + 1);
        policysMapper.updateById(policys);
    }
}
