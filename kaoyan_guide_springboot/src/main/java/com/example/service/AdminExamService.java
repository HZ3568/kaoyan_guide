package com.example.service;

import com.example.mapper.ExamResultMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class AdminExamService {

    private final ExamResultMapper mapper;

    public AdminExamService(ExamResultMapper mapper) {
        this.mapper = mapper;
    }

    /**
     * 管理员分页查询所有用户的考试成绩
     */
    public PageInfo<Map<String, Object>> selectAllResults(int pageNum, int pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Map<String, Object>> list = mapper.selectAllAdminPaged();
        return new PageInfo<>(list);
    }
}
