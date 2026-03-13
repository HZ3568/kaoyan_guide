package com.example.service;

import com.example.entity.*;
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
    private CollectMapper collectMapper;

    @Resource
    private CommentMapper commentMapper;

    public void add(University university) {
        if (university.getIs985() == null) {
            university.setIs985(0);
        }
        if (university.getIs211() == null) {
            university.setIs211(0);
        }
        if (university.getIsDoubleFirstClass() == null) {
            university.setIsDoubleFirstClass(0);
        }
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
        if (university == null) {
            return null;
        }
        if (currentUser != null) {
            Collect collect = collectMapper.selectByUniversityIdAndUserId(university.getId(), currentUser.getId());
            university.setCollectFlag(collect != null);
            Comment comment = commentMapper.selectByUserIdAndUniversityId(currentUser.getId(), id);
            university.setCommentFlag(comment != null);
        } else {
            university.setCollectFlag(false);
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

    public List<University> loadHotUniversity() {
        return universityMapper.loadHotUniversity();
    }
}
