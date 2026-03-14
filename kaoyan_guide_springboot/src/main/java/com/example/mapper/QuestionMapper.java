package com.example.mapper;

import com.example.entity.Question;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface QuestionMapper {
    Question selectById(@Param("id") Long id);

    Question selectRandomEnabled();

    List<Question> selectAll(Question question);

    int insert(Question question);

    int updateById(Question question);

    int deleteById(@Param("id") Long id);
}
