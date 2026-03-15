# 🎓 考研资源整合与学习规划系统 (Kaoyan Guide)

基于 Spring Boot + Vue 3 的前后端分离考研辅导平台。系统创新性地深度集成了 **大语言模型（LLM）**与 **RAG（检索增强生成）** 技术，旨在为考研学子提供智能、精准的一站式资源获取与个性化学习规划服务。

## ✨ 核心亮点 / Features

- 🤖 **AI 智能考研咨询 (Agent & RAG)**：集成大语言模型，并结合本地数据库构建 RAG 检索增强生成。AI 能够根据实时的院校、专业数据，为学生提供精准的择校和报考建议。
- 📅 **AI 智能学习规划**：告别盲目复习，系统可通过大模型分析学生情况，一键生成科学、个性化的每日学习计划（Daily Study Plan）与具体任务拆解。
- 📚 **全面的考研资源大厅**：内置全国高校库、专业门类库，实时更新考研招生政策、官方公告与研招解读。
- 📝 **全方位互动评估**：支持在线模拟考试与成绩评估，提供文章收藏与评论互动功能。
- 🛠️ **强大的后台管理**：面向管理员提供直观的数据统计看板，以及对院校、专业、用户、资讯等全方位的数据管理（CRUD）。

## 🛠️ 技术栈 / Tech Stack

### 后端 (Backend)

- **核心框架**: Java, Spring Boot
- **持久层**: MyBatis / MyBatis-Plus, MySQL
- **缓存 & 状态管理**: Redis (用于数据缓存及 AI 多轮对话的记忆存储)
- **AI 赋能**: LLM API 接入, 自定义 Prompt 工程, RAG 向量检索策略

### 前端 (Frontend)

- **核心框架**: Vue.js, Vite
- **样式**: CSS3, SCSS
- **端侧划分**: 前台门户 (面向学生) + 后台管理系统 (面向管理员)

## 📁 项目结构 / Project Structure

Plaintext

```
kaoyan_guide/
├── kaoyan_guide_springboot/      # 后端工程目录
│   ├── src/main/java/.../
│   │   ├── controller/           # 接口控制层
│   │   ├── service/              # 业务逻辑层 (包含普通业务与大模型交互逻辑)
│   │   │   ├── chat/             # 核心：AI Agent 对话服务、动态 Prompt 构建
│   │   │   └── rag/              # 核心：基于院校知识的 RAG 检索器
│   │   ├── mapper/               # 数据访问层
│   │   ├── entity/               # 实体类
│   │   └── repository/           # Redis 聊天记忆存储等
│   └── src/main/resources/       # 配置文件及 MyBatis XML 映射
├── kaoyan_guide_vue/             # 前端工程目录
│   ├── src/
│   │   ├── views/
│   │   │   ├── front/            # 前台学生端页面 (首页、智能咨询、学习计划等)
│   │   │   └── manager/          # 后台管理端页面 (数据看板、内容管理等)
│   │   └── assets/               # 静态资源与全局样式
└── kaoyan_guide.sql              # 数据库初始化脚本
```

## 🚀 快速开始 / Getting Started

### 1. 环境准备 (Prerequisites)

请确保您的本地环境已安装以下依赖：

- **JDK**: 1.8+ (推荐 JDK 11 或 17)
- **Node.js**: 16.x+ (推荐 18.x)
- **MySQL**: 5.7 或 8.0
- **Redis**: 推荐 6.0+ 并在后台运行

### 2. 数据库配置

1. 在 MySQL 中新建数据库 `kaoyan_guide`。
2. 运行项目根目录下的 `kaoyan_guide.sql` 文件，导入表结构与初始测试数据。

### 3. 后端启动

1. 使用 IDEA 或 Eclipse 打开 `kaoyan_guide_springboot` 目录。
2. 修改 `src/main/resources/application.yml` 中的配置信息：
   - 更新 MySQL 的 `username` 和 `password`。
   - 更新 Redis 的连接信息（如果使用了非默认端口或密码）。
   - （可选）配置您的大模型 API Key。
3. 运行 `SpringbootApplication.java` 启动后端服务。默认运行在 `8080` 端口。

### 4. 前端启动

1. 进入前端目录：

   Bash

   ```
   cd kaoyan_guide_vue
   ```

2. 安装依赖：

   Bash

   ```
   npm install
   ```

3. 启动开发服务器：

   Bash

   ```
   npm run dev
   ```

4. 浏览器访问终端输出的本地地址（如 `http://localhost:5173`）即可使用。

## 📸 系统截图 / Screenshots

*(建议在此处放几张你系统运行时的截图，例如：1. 首页门户 2. AI对话界面 3. 智能学习计划页面 4. 后台数据看板)*

- [截图1：首页]
- [截图2：AI 智能问答]
- [截图3：一键生成学习规划]

## 📄 许可证 / License

本项目为个人毕业设计作品，仅供学习与交流使用。

------

**👨‍💻 开发者**: [你的名字/GitHub ID]

**📧 联系方式**: [你的邮箱或社交链接]

------

### 💡 提示：

- **截图部分**：强烈建议你在项目跑起来后，截几张好看的图（特别是 AI 聊天界面和生成的学习计划界面），把图片放到项目中（比如放一个 `readme_images` 文件夹），然后替换掉 `[截图1]` 这些占位符（例如：`![首页](readme_images/home.png)`）。
- **API Key**：如果你的代码里用到了真实的大模型 API Key，记得在上传 GitHub 前把它写在配置文件里并在 `.gitignore` 中忽略，或者提醒用户自己在 `application.yml` 里填入自己的 Key。
