package com.example.service;

import com.example.entity.ExamResult;
import com.example.mapper.ExamResultMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ExamResultService {

    private final ExamResultMapper mapper;

    public ExamResultService(ExamResultMapper mapper) {
        this.mapper = mapper;
    }

    public void saveResult(ExamResult result) {
        mapper.insertExamResult(result);
    }

    public List<ExamResult> getUserResults(Long userId) {
        return mapper.findByUserId(userId);
    }

    /** 分页查询（PageHelper） */
    public PageInfo<ExamResult> getHistory(Long userId, int pageNum, int pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<ExamResult> list = mapper.findByUserIdPaged(userId);
        return new PageInfo<>(list);
    }

    /** 更新单条（只允许修改自己的记录） */
    public boolean update(ExamResult examResult) {
        return mapper.updateById(examResult) > 0;
    }
}
