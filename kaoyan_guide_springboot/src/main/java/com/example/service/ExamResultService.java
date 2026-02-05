package com.example.service;

import com.example.entity.ExamResult;
import com.example.mapper.ExamResultMapper;
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
}
