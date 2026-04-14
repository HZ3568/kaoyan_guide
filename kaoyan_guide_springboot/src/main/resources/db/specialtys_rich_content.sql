-- 专业信息表新增字段（用于专业详情页 rich content）
-- 执行前请先备份数据

ALTER TABLE `specialtys`
ADD COLUMN IF NOT EXISTS `intro` text COMMENT '专业简介' AFTER `specialty_number`,
ADD COLUMN IF NOT EXISTS `training_objective` text COMMENT '培养目标' AFTER `intro`,
ADD COLUMN IF NOT EXISTS `main_courses` text COMMENT '主要课程' AFTER `training_objective`,
ADD COLUMN IF NOT EXISTS `employment_direction` text COMMENT '就业方向' AFTER `main_courses`,
ADD COLUMN IF NOT EXISTS `official_source_url` varchar(500) DEFAULT NULL COMMENT '官方来源链接' AFTER `employment_direction`;
