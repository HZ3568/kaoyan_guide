# StudyPlan Daily Task 接口文档（设计稿）

## 1. 设计目标

在现有 `study-plan` 模块基础上新增以下能力：

1. 对单个 `daily_task` 进行修改（仅修改 `subject`、`content`）
2. 人工新增单个 `daily_task`
3. 删除单个 `daily_task`
4. 将未完成任务顺延到下一天

说明：当前系统中 `daily_tasks` 存储在 `daily_study_plan.daily_tasks`（JSON 字符串）字段，本设计保持该存储方式不变，通过后端读写 JSON 数组完成单任务操作。

---

## 2. 数据结构约定

### 2.1 DailyTask 对象

```json
{
  "taskId": "9f5d3b2a-2f1e-4f58-9f8f-8f7f2f67f910",
  "subject": "数学",
  "content": "完成高数强化题 20 道",
  "completed": false
}
```

字段说明：

- `taskId`：任务唯一标识，字符串，新增时由后端生成（UUID）
- `subject`：科目，字符串，必填，最大 20 字符
- `content`：任务内容，字符串，必填，最大 200 字符
- `completed`：完成状态，布尔值，默认 `false`

### 2.2 统一响应结构（沿用现有 Result）

```json
{
  "code": "200",
  "msg": "请求成功",
  "data": {}
}
```

---

## 3. 接口清单

### 3.1 新增单个任务

- 方法：`POST`
- 路径：`/study-plan/{date}/tasks`
- 鉴权：学生登录态（与现有 `study-plan` 一致）

请求体：

```json
{
  "subject": "英语",
  "content": "背诵考研词汇 120 个"
}
```

成功响应 `data`：

```json
{
  "taskId": "f4064b8d-8d79-4b03-a9f4-7f5428e03d0a",
  "subject": "英语",
  "content": "背诵考研词汇 120 个",
  "completed": false
}
```

失败场景：

- `date` 格式错误：`code=500, msg=日期格式错误，应为 yyyy-MM-dd`
- 当天计划不存在：`code=500, msg=当日计划不存在，请先生成计划`
- 参数为空或超长：`code=500, msg=参数不合法`

---

### 3.2 修改单个任务（subject/content）

- 方法：`PUT`
- 路径：`/study-plan/{date}/tasks/{taskId}`
- 鉴权：学生登录态

请求体：

```json
{
  "subject": "政治",
  "content": "完成肖八第 2 套选择题"
}
```

成功响应 `data`（返回最新任务对象）：

```json
{
  "taskId": "f4064b8d-8d79-4b03-a9f4-7f5428e03d0a",
  "subject": "政治",
  "content": "完成肖八第 2 套选择题",
  "completed": false
}
```

失败场景：

- 计划不存在：`code=500, msg=当日计划不存在`
- 任务不存在：`code=500, msg=任务不存在`
- 参数不合法：`code=500, msg=参数不合法`

---

### 3.3 删除单个任务

- 方法：`DELETE`
- 路径：`/study-plan/{date}/tasks/{taskId}`
- 鉴权：学生登录态

成功响应：

```json
{
  "code": "200",
  "msg": "请求成功",
  "data": null
}
```

失败场景：

- 计划不存在：`code=500, msg=当日计划不存在`
- 任务不存在：`code=500, msg=任务不存在`

---

### 3.4 未完成任务顺延到下一天

- 方法：`POST`
- 路径：`/study-plan/{date}/tasks/rollover`
- 鉴权：学生登录态
- 语义：把 `{date}` 当天 `completed=false` 的任务迁移到下一天（`date+1`）

请求体（可选）：

```json
{
  "onlyTaskIds": [
    "f4064b8d-8d79-4b03-a9f4-7f5428e03d0a"
  ]
}
```

说明：

- 不传 `onlyTaskIds`：顺延当天所有未完成任务
- 传 `onlyTaskIds`：仅顺延指定任务（且必须为未完成）

成功响应 `data`：

```json
{
  "sourceDate": "2026-03-11",
  "targetDate": "2026-03-12",
  "movedCount": 2,
  "targetTaskTotal": 8
}
```

业务规则：

1. 源日期计划不存在时返回失败
2. 目标日期计划不存在时，自动创建一条新计划记录：
   - `user_feedback` 置空字符串
   - `ai_advice` 固定为 `由前一日未完成任务自动顺延生成`
   - `daily_tasks` 为顺延任务列表
3. 目标日期计划已存在时，追加到原任务列表末尾
4. 顺延时新建任务副本并分配新 `taskId`，`completed=false`
5. 同一请求内不允许重复顺延同一任务

失败场景：

- 无可顺延任务：`code=500, msg=没有可顺延的未完成任务`
- 指定任务不合法：`code=500, msg=指定任务不存在或已完成`

---

## 4. 前端交互建议

1. 任务卡片增加操作按钮：编辑、删除、顺延到明天
2. 增加“新增任务”按钮和弹窗（`subject`、`content`）
3. 编辑弹窗仅允许改 `subject`、`content`
4. 顺延后刷新当前日期与下一日期数据
5. 任务 UI 主键从 `index` 改为 `taskId`

---

## 5. 与现有接口兼容性

1. 保留现有接口不变：
   - `GET /study-plan/{date}`
   - `POST /study-plan/generate`
   - `DELETE /study-plan/{date}`
2. 新增接口全部挂载在 `/study-plan/{date}/tasks` 下，避免破坏既有前端逻辑
3. 旧数据若无 `taskId`，后端读取时自动补齐并回写，保证平滑升级

---

## 6. 实施顺序建议

1. 后端：Controller/Service/Mapper 扩展 + JSON 任务读写工具方法
2. 前端：任务列表主键改造 + 新增/编辑/删除/顺延交互
3. 联调：验证任务增删改与顺延规则、异常提示与刷新逻辑
