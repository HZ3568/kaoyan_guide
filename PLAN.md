# 研途规划 - 管理员后台结构性重构方案

## 一、目标结构

### 五大业务模块

| 模块 | 路径前缀 | 说明 |
|------|----------|------|
| 院校信息管理 | `/admin/school/*` | 原"信息管理"中的学校相关内容 |
| 智能服务管理 | `/admin/ai/*` | AI咨询会话 + 学习规划（新增管理能力）|
| 考场模拟管理 | `/admin/exam/*` | 题库 + 考试数据（新增）|
| 用户管理 | `/admin/user/*` | 管理员 + 学生（路径规范化）|
| 系统内容管理 | `/admin/system/*` | 轮播图 + 系统公告（从"信息管理"迁移）|

---

## 二、路由结构对照表

### 2.1 原路由 → 新路由

| 原路径 | 新路径 | 归属模块 |
|--------|--------|----------|
| `/manager/home` | `/manager/home` | 首页（不变）|
| `/manager/dataStatistics` | `/manager/dataStatistics` | 首页（不变）|
| `/manager/university` | `/manager/school/university` | 院校信息管理 |
| `/manager/areas` | `/manager/school/areas` | 院校信息管理 |
| `/manager/categorys` | `/manager/school/categorys` | 院校信息管理 |
| `/manager/specialtys` | `/manager/school/specialtys` | 院校信息管理 |
| `/manager/interpretations` | `/manager/school/interpretations` | 院校信息管理 |
| `/manager/policys` | `/manager/school/policys` | 院校信息管理 |
| `/manager/comment` | `/manager/school/comment` | 院校信息管理 |
| `/manager/knowledgeBase` | `/manager/ai/knowledgeBase` | 智能服务管理 |
| *(新增)* | `/manager/ai/consultSession` | 智能服务管理 |
| *(新增)* | `/manager/ai/studyPlan` | 智能服务管理 |
| `/manager/question` | `/manager/exam/question` | 考场模拟管理 |
| *(新增)* | `/manager/exam/examData` | 考场模拟管理 |
| `/manager/admin` | `/manager/user/admin` | 用户管理 |
| `/manager/user` | `/manager/user/user` | 用户管理 |
| `/manager/slideshow` | `/manager/system/slideshow` | 系统内容管理 |
| `/manager/notice` | `/manager/system/notice` | 系统内容管理 |
| `/manager/person` | `/manager/person` | 个人中心（不变）|
| `/manager/password` | `/manager/password` | 密码修改（不变）|

### 2.2 路由重定向（兼容旧路径）

在 router/index.js 中**保留旧路径通过 redirect 指向新路径**，实现平滑迁移：
```js
{ path: 'university', redirect: '/manager/school/university' }
// 临时保留12个旧路径重定向（上线后逐步废弃）
```

---

## 三、菜单对照表

### Manager.vue 侧边栏菜单（重构前 → 重构后）

**重构前：**
- 系统首页
- 数据统计（ADMIN）
- 信息管理（ADMIN，12项平铺）
  - 学校信息 / 地区信息 / 门类信息 / 专业信息
  - 专业解读 / 招生政策 / 学校评价
  - 学校专业 / 轮播图信息 / 系统公告
  - 题库管理 / 知识库管理
- 用户管理（ADMIN，2项）
  - 管理员信息 / 学生信息

**重构后：**
- 系统首页
- 数据统计（ADMIN）
- **院校信息管理**（ADMIN，7项）
  - 学校信息 / 地区信息 / 门类信息 / 专业信息
  - 专业解读 / 招生政策 / 院校评价
- **智能服务管理**（ADMIN，3项）⭐新增管理能力
  - 知识库管理 / **咨询会话管理**（新） / **学习规划管理**（新）
- **考场模拟管理**（ADMIN，2项）
  - 题库管理 / **考试数据管理**（新）
- **用户管理**（ADMIN，2项）
  - 管理员信息 / 学生信息
- **系统内容管理**（ADMIN，2项）
  - 轮播图管理 / 系统公告

---

## 四、页面清单

### 4.1 迁移页面（路径变更，组件不动）

| 页面文件 | 原路径 | 新路由路径 |
|----------|--------|-----------|
| `manager/University.vue` | `/manager/university` | `/manager/school/university` |
| `manager/Areas.vue` | `/manager/areas` | `/manager/school/areas` |
| `manager/Categorys.vue` | `/manager/categorys` | `/manager/school/categorys` |
| `manager/Specialtys.vue` | `/manager/specialtys` | `/manager/school/specialtys` |
| `manager/Interpretations.vue` | `/manager/interpretations` | `/manager/school/interpretations` |
| `manager/Policys.vue` | `/manager/policys` | `/manager/school/policys` |
| `manager/Comment.vue` | `/manager/comment` | `/manager/school/comment` |
| `manager/KnowledgeBase.vue` | `/manager/knowledgeBase` | `/manager/ai/knowledgeBase` |
| `manager/Question.vue` | `/manager/question` | `/manager/exam/question` |
| `manager/Admin.vue` | `/manager/admin` | `/manager/user/admin` |
| `manager/User.vue` | `/manager/user` | `/manager/user/user` |
| `manager/Slideshow.vue` | `/manager/slideshow` | `/manager/system/slideshow` |
| `manager/Notice.vue` | `/manager/notice` | `/manager/system/notice` |

### 4.2 新增页面

| 页面文件 | 路由路径 | 说明 | 数据来源 |
|----------|---------|------|----------|
| `manager/ExamData.vue` | `/manager/exam/examData` | 考试数据管理 | `ExamResult` 表 |
| `manager/ConsultSession.vue` | `/manager/ai/consultSession` | 咨询会话管理 | Redis chat memory |
| `manager/StudyPlanManagement.vue` | `/manager/ai/studyPlan` | 学习规划管理 | `DailyStudyPlan` + `StudyPlanTask` 表 |

---

## 五、后端改造

### 5.1 不修改任何现有 Controller

所有现有 Controller 保持不变：
- `UniversityController` → 其接口 `/university/*` 不变
- `QuestionController` → `/question/*` 不变
- `StudyPlanController` → `/study-plan/*` 不变
- `ChatController` → `/chat` 不变
- 等等...

### 5.2 新增 Admin 聚合 Controller

| 文件 | 路径前缀 | 说明 |
|------|----------|------|
| `AdminSchoolController` | `/admin/school` | 聚合学校相关查询（复用现有service）|
| `AdminAiController` | `/admin/ai` | 咨询会话 + 学习规划管理的查询接口 |
| `AdminExamController` | `/admin/exam` | 考试数据的查询/导出接口 |
| `AdminSystemController` | `/admin/system` | 轮播图 + 公告管理的查询接口 |

### 5.3 AdminAiController 新增接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/admin/ai/session/list` | GET | 分页查询会话列表（userId/moduleType/sessionId）|
| `/admin/ai/session/history` | GET | 查看某会话历史消息 |
| `/admin/ai/session/delete` | DELETE | 删除指定会话记录 |
| `/admin/ai/studyPlan/list` | GET | 分页查询所有用户的学习计划 |
| `/admin/ai/studyPlan/task/update` | PUT | 修改任务完成状态 |
| `/admin/ai/studyPlan/task/delete` | DELETE | 删除任务 |
| `/admin/ai/studyPlan/plan/delete` | DELETE | 删除整个计划 |

### 5.4 AdminExamController 新增接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/admin/exam/list` | GET | 分页查询所有用户的考试成绩 |
| `/admin/exam/export` | GET | 管理员导出成绩 Excel |

---

## 六、API 文件

### 新增 Frontend API 文件

| 文件路径 | 导出函数 | 对应后端接口 |
|----------|---------|-------------|
| `src/api/school.js` | 7个查询函数 | `/admin/school/*` |
| `src/api/ai.js` | 7个查询/操作函数 | `/admin/ai/*` |
| `src/api/exam.js` | 2个查询/导出函数 | `/admin/exam/*` |
| `src/api/system.js` | 4个查询函数 | `/admin/system/*` |

---

## 七、Front.vue 顶部导航

`Front.vue` 的水平菜单保持不变（不做结构调整）。

---

## 八、实施顺序

### 第一批（基础框架）
1. 修改 `router/index.js` — 搭建5模块嵌套路由骨架 + 旧路径 redirect
2. 修改 `Manager.vue` — 重构侧边栏菜单为5大模块
3. 新增 3个 API 文件

### 第二批（新增页面）
4. 新增 `ExamData.vue`
5. 新增 `ConsultSession.vue`
6. 新增 `StudyPlanManagement.vue`
7. 新增 4个 AdminController

### 第三批（路由挂载）
8. 将 13个迁移页面挂载到新路由路径
9. 修改各页面内部 `@/api/knowledgeBase.js` 等引用路径（如有）
10. 测试验证

---

## 九、重要约束

1. **不删除** 任何现有 .vue 组件文件
2. **不修改** 任何现有 Controller 的接口路径
3. **不修改** 任何现有 Service 层的业务逻辑
4. 路由变化通过 redirect 兼容旧路径
5. 仅新增文件和修改路由/菜单配置
