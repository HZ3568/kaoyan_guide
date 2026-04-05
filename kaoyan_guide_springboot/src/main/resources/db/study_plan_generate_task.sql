-- 学习计划异步生成任务状态表
-- 执行此脚本以支持 RabbitMQ 异步生成功能
CREATE TABLE IF NOT EXISTS `study_plan_generate_task` (
  `id`           bigint       NOT NULL AUTO_INCREMENT COMMENT '主键',
  `task_id`      varchar(64)  NOT NULL COMMENT '任务唯一标识 (UUID)',
  `user_id`      int          NOT NULL COMMENT '发起用户ID',
  `status`       varchar(20)  NOT NULL DEFAULT 'PENDING' COMMENT '状态: PENDING/RUNNING/SUCCESS/FAILED',
  `message`      varchar(200) NULL     DEFAULT NULL COMMENT '面向用户的状态描述',
  `feedback`     text         NULL     DEFAULT NULL COMMENT '用户昨日反馈',
  `error_info`   text         NULL     DEFAULT NULL COMMENT '失败时的错误信息',
  `created_time` datetime     NOT NULL COMMENT '创建时间',
  `updated_time` datetime     NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_task_id` (`task_id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学习计划异步生成任务状态';
