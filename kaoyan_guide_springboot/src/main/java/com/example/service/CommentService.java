package com.example.service;

import cn.hutool.core.collection.CollectionUtil;
import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.ObjectUtil;
import com.example.entity.Account;
import com.example.entity.Comment;
import com.example.entity.University;
import com.example.exception.CustomException;
import com.example.mapper.CommentMapper;
import com.example.mapper.UniversityMapper;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

/**
 * 学校评价业务处理
 **/
@Service
public class CommentService {

    @Resource
    private CommentMapper commentMapper;

    @Resource
    private UniversityMapper universityMapper;

    /**
     * 新增
     */
    @Transactional
    public void add(Comment comment) {
        comment.setTime(DateUtil.now());
        Comment comment1 = commentMapper.selectByUserIdAndUniversityId(comment.getUserId(), comment.getUniversityId());
        if (ObjectUtil.isNotEmpty(comment1)) {
            throw new CustomException("500", "该学校你已经评价过了。");
        }
        commentMapper.insert(comment);

//        重新计算学校评分
        this.recalculateMark(comment.getUniversityId());
    }

    /**
     * 删除
     */
    @Transactional
    public void deleteById(Integer id) {
        commentMapper.deleteById(id);

        Comment comment = commentMapper.selectById(id);
        //        重新计算学校评分
        this.recalculateMark(comment.getUniversityId());
    }

    /**
     * 批量删除
     */
    @Transactional
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            commentMapper.deleteById(id);
            Comment comment = commentMapper.selectById(id);
            //        重新计算学校评分
            this.recalculateMark(comment.getUniversityId());
        }
    }

    /**
     * 修改
     */
    @Transactional
    public void updateById(Comment comment) {
        commentMapper.updateById(comment);

        //        重新计算学校评分
        this.recalculateMark(comment.getUniversityId());
    }

    /**
     * 根据ID查询
     */
    public Comment selectById(Integer id) {
        return commentMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<Comment> selectAll(Comment comment) {
        return commentMapper.selectAll(comment);
    }

    /**
     * 分页查询
     */
    public PageInfo<Comment> selectPage(Comment comment, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Comment> list = this.selectAll(comment);
        return PageInfo.of(list);
    }

    public void recalculateMark(Integer universityId) {
        List<Comment> commentList = commentMapper.selectByUniversityId(universityId);
        University university = universityMapper.selectById(universityId);
        if (ObjectUtil.isNotEmpty(university)) {
            if (CollectionUtil.isNotEmpty(commentList)) {
                int sum = commentList.stream().mapToInt(x -> x.getMark()).sum();
                university.setMark(new BigDecimal(sum * 1.00 / commentList.size()));
                universityMapper.updateById(university);
            } else {
                university.setMark(new BigDecimal(0));
                universityMapper.updateById(university);
            }
        }
    }

}
