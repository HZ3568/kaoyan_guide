<template>
  <div class="main-content">
    <!-- 顶部 Hero 区域 -->
    <div class="hero-section">
      <!-- 左侧快速导航 -->
      <div class="hero-left card">
        <div class="section-title">
          <el-icon><Menu /></el-icon> <span>快速导航</span>
        </div>
        <div class="nav-list">
          <div class="nav-item" @click="$router.push('/front/universityList')">
            <div class="nav-label">
              <el-icon><School /></el-icon> 查院校
            </div>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </div>
          <div
            class="nav-item"
            @click="$router.push('/front/interpretationsList')"
          >
            <div class="nav-label">
              <el-icon><Reading /></el-icon> 查专业
            </div>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </div>
          <div class="nav-item" @click="$router.push('/front/policysList')">
            <div class="nav-label">
              <el-icon><Document /></el-icon> 招生政策
            </div>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </div>
          <div class="nav-item" @click="$router.push('/front/simulateExam')">
            <div class="nav-label">
              <el-icon><Timer /></el-icon> 模拟考试
            </div>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <!-- 中间轮播图 -->
      <div class="hero-center">
        <el-carousel :interval="4000" height="380px" class="main-carousel">
          <el-carousel-item
            v-for="item in data.slideshowList"
            :key="item.id"
            @click="
              $router.push('/front/universityDetail?id=' + item.universityId)
            "
          >
            <img :src="item.img" alt="轮播图" class="carousel-img" />
            <div class="carousel-overlay">
              <h3>{{ item.title || "开启你的考研成功之路" }}</h3>
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>

      <!-- 右侧公告 -->
      <div class="hero-right card">
        <div class="section-title">
          <div>
            <el-icon><Bell /></el-icon> <span>最新公告</span>
          </div>
          <span class="more-link" @click="$router.push('/front/noticeList')"
            >更多</span
          >
        </div>
        <div class="notice-list">
          <div
            v-for="item in data.noticeList"
            :key="item.id"
            class="notice-item"
            @click="$router.push('/front/noticeList')"
          >
            <span class="notice-dot"></span>
            <span class="notice-title line1">{{ item.title }}</span>
            <span class="notice-time">{{
              item.time ? item.time.substring(5, 10) : ""
            }}</span>
          </div>
        </div>
        <!-- 登录/个人中心引导小卡片 (可选) -->
        <div class="user-action-area" v-if="!data.user.id">
          <el-button
            type="primary"
            round
            class="w-100"
            @click="$router.push('/login')"
            >立即登录</el-button
          >
        </div>
      </div>
    </div>

    <!-- 核心功能入口区 -->
    <div class="core-features-section">
      <div class="section-header-center">
        <h2>核心功能服务</h2>
        <p>AI 赋能考研全流程，打造你的专属上岸计划</p>
      </div>
      <el-row :gutter="20">
        <el-col :span="6">
          <div
            class="feature-card"
            @click="$router.push('/front/consultCollege')"
          >
            <div class="feature-icon blue-bg">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="feature-info">
              <h3>AI 智能咨询</h3>
              <p>24小时在线，解答报考疑惑</p>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="feature-card" @click="$router.push('/front/studyPlan')">
            <div class="feature-icon green-bg">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="feature-info">
              <h3>智能学习规划</h3>
              <p>量身定制，科学安排复习进度</p>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div
            class="feature-card"
            @click="$router.push('/front/universityList')"
          >
            <div class="feature-icon orange-bg">
              <el-icon><School /></el-icon>
            </div>
            <div class="feature-info">
              <h3>院校大数据</h3>
              <p>海量院校库，全方位数据分析</p>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div
            class="feature-card"
            @click="$router.push('/front/simulateExam')"
          >
            <div class="feature-icon purple-bg">
              <el-icon><Edit /></el-icon>
            </div>
            <div class="feature-info">
              <h3>全真模拟考试</h3>
              <p>实战演练，检验复习成果</p>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 平台特色/数据概览 -->
    <div class="platform-stats">
      <div class="stat-item">
        <div class="stat-num">1000+</div>
        <div class="stat-label">收录院校</div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <div class="stat-num">500+</div>
        <div class="stat-label">专业解读</div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <div class="stat-num">10w+</div>
        <div class="stat-label">累计服务考生</div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <div class="stat-num">AI+</div>
        <div class="stat-label">智能驱动</div>
      </div>
    </div>

    <!-- 热门院校 -->
    <div class="content-section">
      <div class="section-header-flex">
        <div class="header-left">
          <span class="title">热门院校</span>
          <span class="subtitle">根据用户满意度与关注度实时推荐</span>
        </div>
        <div
          class="header-right"
          @click="$router.push('/front/universityList')"
        >
          查看更多 <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
      <el-row :gutter="20">
        <el-col :span="12" v-for="item in data.universityList" :key="item.id">
          <div
            class="uni-card card-hover"
            @click="$router.push('/front/universityDetail?id=' + item.id)"
          >
            <img :src="item.avatar" alt="校徽" class="uni-avatar" />
            <div class="uni-info">
              <div class="uni-name">{{ item.name }}</div>
              <div class="uni-tags">
                <el-tag size="small" effect="plain">{{
                  item.schoolType || "院校"
                }}</el-tag>
                <el-tag size="small" effect="plain" type="info">{{
                  item.provinceName || "-"
                }}</el-tag>
                <el-tag
                  size="small"
                  effect="plain"
                  type="danger"
                  v-if="item.is985"
                  >985</el-tag
                >
                <el-tag
                  size="small"
                  effect="plain"
                  type="warning"
                  v-if="item.is211"
                  >211</el-tag
                >
                <el-tag
                  size="small"
                  effect="plain"
                  type="success"
                  v-if="item.isDoubleFirstClass"
                  >双一流</el-tag
                >
              </div>
              <div class="uni-rate">
                <span>办学层次：{{ item.educationLevel || "-" }}</span>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 热门解读 -->
    <div class="content-section bg-light">
      <div class="section-header-flex">
        <div class="header-left">
          <span class="title">热门专业解读</span>
          <span class="subtitle">深度解析热门专业就业前景与考研难度</span>
        </div>
        <div
          class="header-right"
          @click="$router.push('/front/interpretationsList')"
        >
          查看更多 <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
      <el-row :gutter="20">
        <el-col
          :span="8"
          v-for="item in data.interpretationsList"
          :key="item.id"
        >
          <div
            class="inter-card card-hover"
            @click="$router.push('/front/interpretationsDetail?id=' + item.id)"
          >
            <div class="inter-img-box">
              <img :src="item.img" alt="专业图片" class="inter-img" />
              <div class="inter-view">
                <el-icon><View /></el-icon> {{ item.viewCount }}
              </div>
            </div>
            <div class="inter-info">
              <div class="inter-title line1">{{ item.name }}</div>
              <div class="inter-desc line2">{{ item.intro }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import request from "@/utils/request.js";
import { ElMessage } from "element-plus";

const data = reactive({
  user: JSON.parse(localStorage.getItem("xm-user") || "{}"),
  slideshowList: [],
  noticeList: [],
  universityList: [],
  interpretationsList: [],
});

// 获取首页轮播图
const loadSlideshow = () => {
  request.get("/slideshow/selectAll").then((res) => {
    if (res.code === "200") {
      data.slideshowList = res.data;
    } else {
      ElMessage.error(res.msg);
    }
  });
};
loadSlideshow();

// 获取最新公告
const loadNotice = () => {
  request.get("/notice/selectAll").then((res) => {
    if (res.code === "200") {
      data.noticeList = res.data.splice(0, 5); // 稍微多展示一条
    } else {
      ElMessage.error(res.msg);
    }
  });
};
loadNotice();

// 满意度最高的前6个学校
const loadHotUniversity = () => {
  request.get("/university/loadHotUniversity").then((res) => {
    if (res.code === "200") {
      data.universityList = res.data;
    } else {
      ElMessage.error(res.msg);
    }
  });
};
loadHotUniversity();

// 浏览量前6的专业解读
const loadHotInterpretations = () => {
  request.get("/interpretations/loadHotInterpretations").then((res) => {
    if (res.code === "200") {
      data.interpretationsList = res.data;
    } else {
      ElMessage.error(res.msg);
    }
  });
};
loadHotInterpretations();
</script>

<style scoped>
.main-content {
  min-height: 100vh;
}

/* 通用卡片样式 */
.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.card-hover {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  cursor: pointer;
}

.card-hover:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.line1 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.line2 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

/* 顶部 Hero 区域 */
.hero-section {
  display: flex;
  gap: 20px;
  margin-bottom: 40px;
  height: 380px;
}

.hero-left {
  width: 260px;
  display: flex;
  flex-direction: column;
}

.hero-center {
  flex: 1;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.hero-right {
  width: 280px;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #333;
}

.section-title .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.more-link {
  font-size: 14px;
  color: #999;
  cursor: pointer;
  font-weight: normal;
}

.more-link:hover {
  color: #409eff;
}

/* 导航列表 */
.nav-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
}

.nav-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.nav-item:hover {
  background: #f5f7fa;
}

.nav-label {
  display: flex;
  align-items: center;
  font-size: 16px;
  color: #333;
}

.nav-label .el-icon {
  margin-right: 10px;
  font-size: 18px;
  color: #666;
}

.nav-item .arrow {
  color: #ccc;
}

/* 轮播图 */
.main-carousel {
  border-radius: 8px;
}

.carousel-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.carousel-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
  padding: 20px;
  color: #fff;
}

.carousel-overlay h3 {
  margin: 0;
  font-size: 20px;
}

/* 公告列表 */
.notice-list {
  flex: 1;
  overflow: hidden;
}

.notice-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  cursor: pointer;
  font-size: 14px;
}

.notice-item:hover .notice-title {
  color: #409eff;
}

.notice-dot {
  width: 6px;
  height: 6px;
  background: #e4e7ed;
  border-radius: 50%;
  margin-right: 10px;
}

.notice-item:hover .notice-dot {
  background: #409eff;
}

.notice-title {
  flex: 1;
  color: #606266;
}

.notice-time {
  color: #999;
  font-size: 12px;
  margin-left: 10px;
}

.user-action-area {
  margin-top: 10px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.w-100 {
  width: 100%;
}

/* 核心功能区 */
.core-features-section {
  margin-bottom: 50px;
}

.section-header-center {
  text-align: center;
  margin-bottom: 30px;
}

.section-header-center h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.section-header-center p {
  color: #666;
  font-size: 16px;
}

.feature-card {
  background: #fff;
  border-radius: 12px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #ebeef5;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
  border-color: #dcdfe6;
}

.feature-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  color: #fff;
}

.blue-bg {
  background: linear-gradient(135deg, #36d1dc, #5b86e5);
}
.green-bg {
  background: linear-gradient(135deg, #42e695, #3bb2b8);
}
.orange-bg {
  background: linear-gradient(135deg, #ff9a9e, #fecfef);
  color: #fff;
  background-color: #ff9900;
  background: linear-gradient(135deg, #ffb75e, #ed8f03);
}
.purple-bg {
  background: linear-gradient(135deg, #a18cd1, #fbc2eb);
}

.feature-info h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
  color: #333;
}

.feature-info p {
  margin: 0;
  font-size: 13px;
  color: #999;
}

/* 平台数据/特色 */
.platform-stats {
  background: linear-gradient(to right, #409eff, #337ecc);
  border-radius: 12px;
  padding: 30px;
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin-bottom: 50px;
  color: #fff;
}

.stat-item {
  text-align: center;
}

.stat-num {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.3);
}

/* 热门院校 & 解读通用 */
.content-section {
  margin-bottom: 50px;
}

.section-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 25px;
}

.section-header-flex .title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-right: 15px;
}

.section-header-flex .subtitle {
  color: #999;
  font-size: 14px;
}

.header-right {
  color: #606266;
  cursor: pointer;
  display: flex;
  align-items: center;
  font-size: 14px;
}

.header-right:hover {
  color: #409eff;
}

/* 院校卡片 */
.uni-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  margin-bottom: 20px;
}

.uni-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 2px solid #f5f7fa;
}

.uni-info {
  flex: 1;
}

.uni-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.uni-tags {
  margin-bottom: 8px;
}

.uni-tags .el-tag {
  margin-right: 8px;
}

.uni-rate {
  font-size: 13px;
  color: #666;
  display: flex;
  align-items: center;
}

/* 解读卡片 */
.inter-card {
  padding: 0;
  overflow: hidden;
  margin-bottom: 20px;
}

.inter-img-box {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.inter-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.inter-card:hover .inter-img {
  transform: scale(1.05);
}

.inter-view {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  padding: 5px 10px;
  font-size: 12px;
  display: flex;
  align-items: center;
}

.inter-view .el-icon {
  margin-right: 5px;
}

.inter-info {
  padding: 15px;
}

.inter-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.inter-desc {
  font-size: 13px;
  color: #888;
  line-height: 1.5;
}
</style>
