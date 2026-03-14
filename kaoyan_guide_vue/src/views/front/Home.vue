<template>
  <div class="main-content">
    <!-- 顶部 Hero 区域 -->
    <div class="hero-section">
      <!-- 左侧公告 -->
      <div class="hero-left card">
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

      <!-- 右侧每日一题 -->
      <div class="hero-right card">
        <div class="section-title">
          <div>
            <el-icon><EditPen /></el-icon> <span>每日一题</span>
          </div>
          <el-tag size="small" type="warning" effect="plain">{{
            data.dailyQuestion?.difficulty || "medium"
          }}</el-tag>
        </div>
        <div class="daily-question-box" v-loading="data.dailyLoading">
          <div v-if="data.dailyQuestion">
            <div class="daily-meta">
              <el-tag size="small" effect="plain">{{
                data.dailyQuestion.subject
              }}</el-tag>
              <el-tag size="small" type="success" effect="plain">{{
                formatQuestionType(data.dailyQuestion.type)
              }}</el-tag>
            </div>
            <div class="daily-title">
              <MathContent :content="data.dailyQuestion.title" />
            </div>

            <div
              class="daily-options"
              v-if="
                data.dailyQuestion.type !== 'short_answer' &&
                (data.dailyQuestion.optionA || data.dailyQuestion.optionB)
              "
            >
              <el-radio-group
                v-model="data.answerDraft"
                :disabled="data.dailyHasAnswered || data.submitting"
              >
                <el-radio
                  v-if="data.dailyQuestion.optionA"
                  label="A"
                  border
                  class="daily-option-item"
                >
                  <div class="daily-option-content">
                    <span class="daily-option-prefix">A.</span>
                    <MathContent :content="data.dailyQuestion.optionA" />
                  </div>
                </el-radio>
                <el-radio
                  v-if="data.dailyQuestion.optionB"
                  label="B"
                  border
                  class="daily-option-item"
                >
                  <div class="daily-option-content">
                    <span class="daily-option-prefix">B.</span>
                    <MathContent :content="data.dailyQuestion.optionB" />
                  </div>
                </el-radio>
                <el-radio
                  v-if="data.dailyQuestion.optionC"
                  label="C"
                  border
                  class="daily-option-item"
                >
                  <div class="daily-option-content">
                    <span class="daily-option-prefix">C.</span>
                    <MathContent :content="data.dailyQuestion.optionC" />
                  </div>
                </el-radio>
                <el-radio
                  v-if="data.dailyQuestion.optionD"
                  label="D"
                  border
                  class="daily-option-item"
                >
                  <div class="daily-option-content">
                    <span class="daily-option-prefix">D.</span>
                    <MathContent :content="data.dailyQuestion.optionD" />
                  </div>
                </el-radio>
              </el-radio-group>
            </div>

            <el-input
              v-if="data.dailyQuestion.type === 'short_answer'"
              v-model="data.answerDraft"
              type="textarea"
              :rows="3"
              placeholder="请输入你的答案"
              :disabled="data.dailyHasAnswered || data.submitting"
            />

            <div class="daily-submit-area" v-if="!data.dailyHasAnswered">
              <el-button
                type="primary"
                class="w-100"
                :loading="data.submitting"
                @click="submitTodayAnswer"
                >提交答案</el-button
              >
            </div>

            <div class="daily-result" v-if="data.dailyHasAnswered">
              <el-alert
                :title="
                  data.dailyResult?.isCorrect
                    ? '回答正确，继续加油！'
                    : '回答错误，再接再厉！'
                "
                :type="data.dailyResult?.isCorrect ? 'success' : 'error'"
                :closable="false"
                show-icon
              />
              <div class="daily-result-item">
                <span>你的答案：</span>
                <MathContent
                  class="daily-inline-content"
                  inline
                  :content="data.dailyResult?.userAnswer || '-'"
                />
              </div>
              <div class="daily-result-item">
                <span>正确答案：</span>
                <MathContent
                  class="daily-inline-content"
                  inline
                  :content="data.dailyResult?.correctAnswer || '-'"
                />
              </div>
              <div class="daily-analysis">
                <span>解析：</span>
                <MathContent
                  class="daily-inline-content"
                  :content="data.dailyResult?.analysis || '暂无解析'"
                />
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无题目，稍后再来" :image-size="90" />
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
import MathContent from "@/components/MathContent.vue";

const data = reactive({
  user: JSON.parse(localStorage.getItem("xm-user") || "{}"),
  slideshowList: [],
  noticeList: [],
  universityList: [],
  interpretationsList: [],
  dailyQuestion: null,
  dailyHasAnswered: false,
  dailyResult: null,
  answerDraft: "",
  dailyLoading: false,
  submitting: false,
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

const formatQuestionType = (type) => {
  if (type === "single_choice") return "单选题";
  if (type === "judge") return "判断题";
  if (type === "short_answer") return "简答题";
  return "题目";
};

const loadDailyQuestion = () => {
  data.dailyLoading = true;
  request
    .get("/daily-question/today")
    .then((res) => {
      if (res.code === "200") {
        data.dailyQuestion = res.data?.question || null;
        data.dailyHasAnswered = !!res.data?.hasAnswered;
        data.dailyResult = res.data?.answerResult || null;
      } else {
        ElMessage.error(res.msg);
      }
    })
    .finally(() => {
      data.dailyLoading = false;
    });
};
loadDailyQuestion();

const submitTodayAnswer = () => {
  if (!data.user.id) {
    ElMessage.warning("请先登录后再作答");
    return;
  }
  if (!data.answerDraft || !data.answerDraft.trim()) {
    ElMessage.warning("请先作答后再提交");
    return;
  }
  data.submitting = true;
  request
    .post("/daily-question/submit", { answer: data.answerDraft.trim() })
    .then((res) => {
      if (res.code === "200") {
        data.dailyHasAnswered = true;
        data.dailyResult = res.data;
        ElMessage.success("提交成功");
      } else {
        ElMessage.error(res.msg);
      }
    })
    .finally(() => {
      data.submitting = false;
    });
};

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
  width: 280px;
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

.daily-question-box {
  flex: 1;
  overflow: auto;
}

.daily-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.daily-title {
  color: #303133;
  line-height: 1.7;
  font-size: 14px;
  margin-bottom: 14px;
}

.daily-options :deep(.el-radio-group) {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.daily-option-item {
  margin-right: 0;
  width: 100%;
}

.daily-option-content {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  width: 100%;
}

.daily-option-prefix {
  color: #303133;
  font-weight: 600;
  flex-shrink: 0;
}

.daily-submit-area {
  margin-top: 14px;
}

.daily-result {
  margin-top: 14px;
}

.daily-result-item,
.daily-analysis {
  margin-top: 10px;
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
}

.daily-inline-content {
  display: inline;
}

.daily-result-item span,
.daily-analysis span {
  color: #303133;
  font-weight: 600;
}

.daily-options :deep(.el-radio__label) {
  display: block;
  width: calc(100% - 24px);
  white-space: normal;
}

.daily-question-box :deep(.katex-display) {
  max-width: 100%;
}

@media (max-width: 1400px) {
  .hero-section {
    gap: 14px;
  }

  .hero-left,
  .hero-right {
    width: 260px;
  }
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
