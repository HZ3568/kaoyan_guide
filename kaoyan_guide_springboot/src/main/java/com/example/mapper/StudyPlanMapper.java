package com.example.mapper;

import com.example.entity.DailyStudyPlan;
import com.example.entity.StudyPlanTask;
import org.apache.ibatis.annotations.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@Mapper
public interface StudyPlanMapper {

        /**
         * 插入新的学习计划
         */
        @Insert("INSERT INTO study_plan (user_id, plan_date, user_feedback, ai_advice, plan_status, create_time, update_time) "
                        +
                        "VALUES (#{userId}, #{planDate}, #{userFeedback}, #{aiAdvice}, #{planStatus}, #{createTime}, #{updateTime})")
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

        @Insert("INSERT INTO study_plan_task (task_id, plan_id, subject, content, completed, task_source, sort_no, create_time, update_time) "
                        +
                        "VALUES (#{taskId}, #{planId}, #{subject}, #{content}, #{completed}, #{taskSource}, #{sortNo}, #{createTime}, #{updateTime})")
        void insertTask(StudyPlanTask task);

        /**
         * 批量插入任务（用于 replacePlanTasks 减少 N 次 DB 调用）
         */
        @Insert("<script>" +
                "INSERT INTO study_plan_task (task_id, plan_id, subject, content, completed, task_source, sort_no, create_time, update_time) VALUES " +
                "<foreach collection='tasks' item='t' separator=','>" +
                "(#{t.taskId}, #{t.planId}, #{t.subject}, #{t.content}, #{t.completed}, #{t.taskSource}, #{t.sortNo}, #{t.createTime}, #{t.updateTime})" +
                "</foreach>" +
                "</script>")
        void batchInsertTasks(@Param("tasks") List<StudyPlanTask> tasks);

        @Select("SELECT * FROM study_plan_task WHERE plan_id = #{planId} ORDER BY sort_no ASC, id ASC")
        List<StudyPlanTask> selectTasksByPlanId(@Param("planId") Long planId);

        /**
         * 批量查询多个计划的任务（避免 N+1）
         */
        @Select("<script>" +
                "SELECT * FROM study_plan_task WHERE plan_id IN " +
                "<foreach collection='planIds' item='planId' open='(' separator=',' close=')'>" +
                "#{planId}" +
                "</foreach>" +
                " ORDER BY plan_id ASC, sort_no ASC, id ASC" +
                "</script>")
        List<StudyPlanTask> selectTasksByPlanIds(@Param("planIds") List<Long> planIds);

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

        @Update("UPDATE study_plan SET user_feedback = #{userFeedback}, ai_advice = #{aiAdvice}, plan_status = #{planStatus}, update_time = #{updateTime} WHERE id = #{id}")
        int updatePlanCoreById(DailyStudyPlan plan);

        @Update("UPDATE study_plan SET plan_status = #{planStatus}, update_time = #{updateTime} WHERE id = #{id}")
        int updatePlanStatusById(@Param("id") Long id, @Param("planStatus") String planStatus,
                        @Param("updateTime") java.time.LocalDateTime updateTime);

        /**
         * 根据 planId 统计任务数量和完成数量，回写主表状态
         */
        @Select("SELECT COUNT(*) FROM study_plan_task WHERE plan_id = #{planId}")
        int countTasksByPlanId(@Param("planId") Long planId);

        @Select("SELECT COUNT(*) FROM study_plan_task WHERE plan_id = #{planId} AND completed = 1")
        int countCompletedTasksByPlanId(@Param("planId") Long planId);

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

        // ==================== 管理员接口 ====================

        /**
         * 查询所有用户的学习计划（分页）
         * 显式别名保证 MyBatis 返回 camelCase 键名，与前端字段一致
         */
        @Select("SELECT p.id AS planId, p.user_id AS userId, p.plan_date AS planDate, " +
                "p.user_feedback AS userFeedback, p.ai_advice AS aiAdvice, " +
                "p.plan_status AS planStatus, " +
                "p.create_time AS createTime, p.update_time AS updateTime, " +
                "u.name AS userName " +
                "FROM study_plan p LEFT JOIN user u ON p.user_id = u.id " +
                "ORDER BY p.plan_date DESC")
        List<Map<String, Object>> selectAllAdminPaged();

        /**
         * 根据 ID 查询单条计划（含完整字段，用于管理员详情）
         */
        @Select("SELECT p.id AS planId, p.user_id AS userId, p.plan_date AS planDate, " +
                "p.user_feedback AS userFeedback, p.ai_advice AS aiAdvice, " +
                "p.plan_status AS planStatus, " +
                "p.create_time AS createTime, p.update_time AS updateTime, " +
                "u.name AS userName " +
                "FROM study_plan p LEFT JOIN user u ON p.user_id = u.id " +
                "WHERE p.id = #{planId}")
        Map<String, Object> selectAdminDetailById(@Param("planId") Long planId);

        /**
         * 查询所有用户的学习计划总数
         */
        @Select("SELECT COUNT(*) FROM study_plan")
        long countAllAdmin();

        /**
         * 管理员删除指定用户指定日期的计划
         */
        @Delete("DELETE FROM study_plan WHERE user_id = #{userId} AND plan_date = #{date}")
        void deleteByDateAdmin(@Param("userId") Integer userId, @Param("date") LocalDate date);

        /**
         * 管理员修改任务完成状态
         */
        @Update("UPDATE study_plan_task SET completed = #{completed}, update_time = NOW() " +
                "WHERE plan_id = #{planId} AND task_id = #{taskId}")
        int updateTaskCompletedAdmin(@Param("planId") Long planId, @Param("taskId") String taskId,
                        @Param("completed") Boolean completed);
}
