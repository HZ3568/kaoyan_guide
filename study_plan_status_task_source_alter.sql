ALTER TABLE study_plan
ADD COLUMN plan_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' AFTER ai_advice;

ALTER TABLE study_plan_task
ADD COLUMN task_source VARCHAR(20) NOT NULL DEFAULT 'GENERATED' AFTER completed;

UPDATE study_plan
SET plan_status = 'GENERATED'
WHERE plan_status IS NULL OR plan_status = '';

UPDATE study_plan_task
SET task_source = 'GENERATED'
WHERE task_source IS NULL OR task_source = '';
