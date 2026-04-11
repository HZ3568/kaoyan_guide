package com.example.mapper;

import com.example.entity.ExamResult;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface ExamResultMapper {

    // 保存成绩
    void insertExamResult(ExamResult examResult);

    // 查询用户成绩列表（全部，按时间倒序）
    List<ExamResult> findByUserId(@Param("userId") Long userId);

    // 分页查询（由 PageHelper 拦截，不需要额外参数）
    List<ExamResult> findByUserIdPaged(@Param("userId") Long userId);

    // 更新单条记录（只允许修改自己的）
    int updateById(ExamResult examResult);
}
