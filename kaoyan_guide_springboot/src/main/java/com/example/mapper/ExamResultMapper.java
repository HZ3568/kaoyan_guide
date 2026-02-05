package com.example.mapper;

import com.example.entity.ExamResult;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface ExamResultMapper {

    // 保存成绩
    void insertExamResult(ExamResult examResult);

    // 查询用户成绩列表
    List<ExamResult> findByUserId(@Param("userId") Long userId);
}
