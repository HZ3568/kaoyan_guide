package com.example.mapper;

import com.example.entity.DailyStudyPlan;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.time.LocalDate;
import java.util.List;

@Mapper
public interface StudyPlanMapper {

    /**
     * 插入新的学习计划
     */
    @Insert("INSERT INTO daily_study_plan (user_id, plan_date, user_feedback, ai_advice, daily_tasks, create_time) " +
            "VALUES (#{userId}, #{planDate}, #{userFeedback}, #{aiAdvice}, #{dailyTasks}, #{createTime})")
    void insert(DailyStudyPlan plan);

    /**
     * 根据用户ID和日期删除计划
     */
    @Delete("DELETE FROM daily_study_plan WHERE user_id = #{userId} AND plan_date = #{date}")
    void deleteByDate(@Param("userId") Integer userId, @Param("date") LocalDate date);

    /**
     * 根据用户ID和日期查询计划
     */
    @Select("SELECT * FROM daily_study_plan WHERE user_id = #{userId} AND plan_date = #{date}")
    DailyStudyPlan selectByDate(@Param("userId") Integer userId, @Param("date") LocalDate date);

    /**
     * 查询指定日期范围内的历史计划
     */
    @Select("SELECT * FROM daily_study_plan WHERE user_id = #{userId} AND plan_date BETWEEN #{startDate} AND #{endDate} ORDER BY plan_date ASC")
    List<DailyStudyPlan> selectHistory(@Param("userId") Integer userId, @Param("startDate") LocalDate startDate,
            @Param("endDate") LocalDate endDate);
}
