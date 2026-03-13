package com.example.mapper;

import com.example.entity.DailyStudyPlan;
import com.example.entity.StudyPlanTask;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Options;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.time.LocalDate;
import java.util.List;

@Mapper
public interface StudyPlanMapper {

        /**
         * 插入新的学习计划
         */
        @Insert("INSERT INTO study_plan (user_id, plan_date, user_feedback, ai_advice, create_time, update_time) " +
                        "VALUES (#{userId}, #{planDate}, #{userFeedback}, #{aiAdvice}, #{createTime}, #{updateTime})")
        @Options(useGeneratedKeys = true, keyProperty = "id", keyColumn = "id")
        void insert(DailyStudyPlan plan);

        /**
         * 根据用户ID和日期删除计划
         */
        @Delete("DELETE FROM study_plan WHERE user_id = #{userId} AND plan_date = #{date}")
        void deleteByDate(@Param("userId") Integer userId, @Param("date") LocalDate date);

        /**
         * 根据用户ID和日期查询计划
         */
        @Select("SELECT * FROM study_plan WHERE user_id = #{userId} AND plan_date = #{date}")
        DailyStudyPlan selectByDate(@Param("userId") Integer userId, @Param("date") LocalDate date);

        /**
         * 查询指定日期范围内的历史计划
         */
        @Select("SELECT * FROM study_plan WHERE user_id = #{userId} AND plan_date BETWEEN #{startDate} AND #{endDate} ORDER BY plan_date ASC")
        List<DailyStudyPlan> selectHistory(@Param("userId") Integer userId, @Param("startDate") LocalDate startDate,
                        @Param("endDate") LocalDate endDate);

        @Insert("INSERT INTO study_plan_task (task_id, plan_id, subject, content, completed, sort_no, create_time, update_time) "
                        +
                        "VALUES (#{taskId}, #{planId}, #{subject}, #{content}, #{completed}, #{sortNo}, #{createTime}, #{updateTime})")
        void insertTask(StudyPlanTask task);

        @Select("SELECT * FROM study_plan_task WHERE plan_id = #{planId} ORDER BY sort_no ASC, id ASC")
        List<StudyPlanTask> selectTasksByPlanId(@Param("planId") Long planId);

        @Update("<script>" +
                        "UPDATE study_plan_task " +
                        "SET sort_no = CASE task_id " +
                        "<foreach collection='taskIds' item='taskId' index='index'>" +
                        "WHEN #{taskId} THEN #{index} " +
                        "</foreach>" +
                        "END " +
                        "WHERE plan_id = #{planId} AND task_id IN " +
                        "<foreach collection='taskIds' item='taskId' open='(' separator=',' close=')'>" +
                        "#{taskId}" +
                        "</foreach>" +
                        "</script>")
        void updateTaskSortByTaskIds(@Param("planId") Long planId, @Param("taskIds") List<String> taskIds);

        @Update("UPDATE study_plan_task SET subject = #{subject}, content = #{content} " +
                        "WHERE plan_id = #{planId} AND task_id = #{taskId}")
        int updateTaskByPlanIdAndTaskId(@Param("planId") Long planId, @Param("taskId") String taskId,
                        @Param("subject") String subject, @Param("content") String content);

        @Update("UPDATE study_plan_task SET completed = #{completed} " +
                        "WHERE plan_id = #{planId} AND task_id = #{taskId}")
        int updateTaskCompletedByPlanIdAndTaskId(@Param("planId") Long planId, @Param("taskId") String taskId,
                        @Param("completed") Boolean completed);

        @Delete("DELETE FROM study_plan_task WHERE plan_id = #{planId} AND task_id = #{taskId}")
        int deleteTaskByPlanIdAndTaskId(@Param("planId") Long planId, @Param("taskId") String taskId);

        @Delete("<script>" +
                        "DELETE FROM study_plan_task WHERE plan_id = #{planId} AND task_id IN " +
                        "<foreach collection='taskIds' item='taskId' open='(' separator=',' close=')'>" +
                        "#{taskId}" +
                        "</foreach>" +
                        "</script>")
        int deleteTasksByPlanIdAndTaskIds(@Param("planId") Long planId, @Param("taskIds") List<String> taskIds);

        @Delete("DELETE FROM study_plan_task WHERE plan_id = #{planId}")
        void deleteTasksByPlanId(@Param("planId") Long planId);
}
