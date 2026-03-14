package com.example.mapper;

import com.example.entity.QuestionRecord;
import org.apache.ibatis.annotations.Param;

import java.time.LocalDate;

public interface QuestionRecordMapper {
    QuestionRecord selectByUserAndDate(@Param("userId") Long userId, @Param("questionDate") LocalDate questionDate);

    int insert(QuestionRecord questionRecord);
}
