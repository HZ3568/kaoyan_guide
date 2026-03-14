package com.example.mapper;

import com.example.entity.DailyQuestion;
import org.apache.ibatis.annotations.Param;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

public interface DailyQuestionMapper {
    DailyQuestion selectByDate(@Param("questionDate") LocalDate questionDate);

    int insert(DailyQuestion dailyQuestion);

    int updateByDate(DailyQuestion dailyQuestion);

    List<Map<String, Object>> selectRecentAssignments(@Param("startDate") LocalDate startDate,
                                                      @Param("endDate") LocalDate endDate);
}
