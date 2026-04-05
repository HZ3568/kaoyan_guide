package com.example.mapper;

import com.example.entity.StudyPlanGenerateTask;
import org.apache.ibatis.annotations.*;

@Mapper
public interface StudyPlanGenerateTaskMapper {

    @Insert("INSERT INTO study_plan_generate_task " +
            "(task_id, user_id, status, message, feedback, error_info, created_time, updated_time) " +
            "VALUES (#{taskId}, #{userId}, #{status}, #{message}, #{feedback}, #{errorInfo}, #{createdTime}, #{updatedTime})")
    @Options(useGeneratedKeys = true, keyProperty = "id", keyColumn = "id")
    void insert(StudyPlanGenerateTask task);

    @Select("SELECT * FROM study_plan_generate_task WHERE task_id = #{taskId}")
    StudyPlanGenerateTask selectByTaskId(@Param("taskId") String taskId);

    @Update("UPDATE study_plan_generate_task " +
            "SET status = #{status}, message = #{message}, error_info = #{errorInfo}, updated_time = #{updatedTime} " +
            "WHERE task_id = #{taskId}")
    void updateStatus(@Param("taskId") String taskId,
                      @Param("status") String status,
                      @Param("message") String message,
                      @Param("errorInfo") String errorInfo,
                      @Param("updatedTime") java.time.LocalDateTime updatedTime);
}
