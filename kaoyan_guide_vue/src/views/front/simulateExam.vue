<template>
  <div class="main-content exam-page" ref="examPageRef">
    <div class="content-wrapper">
      <!-- 左侧：模拟数据分析看板 -->
      <div class="dashboard-panel">
        <div class="panel-header">
          <h3>
            <el-icon><DataLine /></el-icon> 模拟数据分析
          </h3>
          <!-- 近五次 / 全部 切换 -->
          <div class="view-tabs">
            <span class="view-tab active">近五次</span>
            <span class="view-tab" @click="$router.push('/front/simulateExamHistory')">全部</span>
          </div>
        </div>

        <!-- 科目切换 -->
        <div class="subject-tabs">
          <div
            v-for="sub in ['政治', '英语', '数学', '专业课']"
            :key="sub"
            :class="['tab-item', { active: chartSubject === sub }]"
            @click="changeSubject(sub)"
          >
            {{ sub }}
          </div>
        </div>

        <!-- 图表区域 -->
        <div class="chart-container">
          <div class="chart-box">
            <h4>得分趋势</h4>
            <div ref="scoreChartRef" class="chart"></div>
          </div>
          <div class="chart-box">
            <h4>用时分析 (min)</h4>
            <div ref="timeChartRef" class="chart"></div>
          </div>
        </div>
      </div>

      <!-- 右侧：考试模拟器 -->
      <div class="exam-panel">
        <div class="exam-container">
          <div class="exam-header">
            <el-select
              v-model="examMode"
              placeholder="演示模式"
              style="width: 180px"
              :disabled="data.isStarted"
            >
              <el-option label="演示模式 (1分钟)" :value="60" />
              <el-option label="标准模式 (3小时)" :value="10800" />
            </el-select>
          </div>

          <div
            class="timer-display"
            :class="{ 'time-warning': data.remainingSeconds < 300 }"
          >
            {{ formattedTime }}
          </div>

          <div class="exam-status-text" v-if="data.isStarted && !data.isFinished">
            正在进行考试...
          </div>
          <div class="exam-status-text finished" v-if="data.isFinished">
            考试已结束
          </div>

          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: progressPercentage + '%' }"
              :class="{ warning: data.remainingSeconds < 1800 }"
            ></div>
          </div>

          <div class="exam-buttons">
            <el-button
              type="success"
              size="large"
              class="action-btn start-btn"
              :disabled="data.isStarted && !data.isFinished"
              @click="startExam"
            >
              <el-icon><VideoPlay /></el-icon> 开始答题
            </el-button>

            <el-button
              type="info"
              size="large"
              class="action-btn stop-btn"
              :disabled="!data.isStarted || data.isFinished"
              @click="finishExam"
            >
              <el-icon><VideoPause /></el-icon> 完成答题
            </el-button>

            <el-button
              type="primary"
              size="large"
              class="action-btn screen-btn"
              @click="toggleFullscreen"
            >
              <el-icon><FullScreen /></el-icon>
              {{ isFullscreen ? "退出全屏" : "进入全屏" }}
            </el-button>
          </div>

          <p class="footer-tip">准备就绪，请保持专注</p>

          <div v-if="data.isFinished" class="result-summary">
            <p>本次用时：<span>{{ data.durationText }}</span></p>
          </div>
        </div>
      </div>
    </div>

    <!-- 交卷弹窗 -->
    <el-dialog
      title="考试结果提交"
      v-model="dialogVisible"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="80px">
        <el-form-item label="考试科目">
          <el-select v-model="formData.subject" placeholder="请选择考试科目" style="width: 100%">
            <el-option label="政治" value="政治" />
            <el-option label="英语" value="英语" />
            <el-option label="数学" value="数学" />
            <el-option label="专业课" value="专业课" />
          </el-select>
        </el-form-item>

        <el-form-item label="试题出处">
          <el-input v-model="formData.questionSource" placeholder="请输入试题出处（必填）" />
        </el-form-item>

        <el-form-item label="考试成绩">
          <el-input
            v-model.number="formData.score"
            placeholder="请输入考试成绩"
            type="number"
            min="0"
            max="150"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitResult">提交记录</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, computed, ref, watch, onMounted, onUnmounted, nextTick } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { DataLine, VideoPlay, VideoPause, FullScreen } from "@element-plus/icons-vue";
import request from "@/utils/request";
import * as echarts from "echarts";

const router = useRouter();

// ================== 用户信息 ==================
const user = JSON.parse(localStorage.getItem("xm-user") || "{}");

// ================== 响应式状态 ==================
const examMode = ref(60);

// 切换模式时，若未开始考试，立即更新剩余时间显示
watch(examMode, (newVal) => {
  if (!data.isStarted) {
    data.remainingSeconds = newVal;
    data.totalDuration = newVal;
  }
});

const data = reactive({
  isStarted: false,
  isFinished: false,
  startTime: null,
  endTime: null,
  remainingSeconds: 60,
  timer: null,
  durationText: "",
  durationSeconds: 0,
  totalDuration: 60,
});

const dialogVisible = ref(false);
const formData = reactive({
  subject: "",
  questionSource: "",
  score: null,
});

// ================== 图表相关状态 ==================
const chartSubject = ref("政治");
const examHistory = ref([]);
const scoreChartRef = ref(null);
const timeChartRef = ref(null);
let scoreChart = null;
let timeChart = null;

// ================== 计算属性 ==================
const formattedTime = computed(() => {
  const h = Math.floor(data.remainingSeconds / 3600);
  const m = Math.floor((data.remainingSeconds % 3600) / 60);
  const s = data.remainingSeconds % 60;
  return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
});

const progressPercentage = computed(() => {
  if (!data.isStarted) return 0;
  const elapsed = data.totalDuration - data.remainingSeconds;
  return Math.min(100, (elapsed / data.totalDuration) * 100);
});

// ================== 图表逻辑 ==================
const loadExamHistory = () => {
  if (!user.id) return;
  request.get("/exam/list", { params: { userId: user.id } }).then((res) => {
    if (res.code === "200") {
      examHistory.value = res.data || [];
      updateCharts();
    }
  });
};

const changeSubject = (sub) => {
  chartSubject.value = sub;
  updateCharts();
};

const updateCharts = () => {
  if (!scoreChart || !timeChart) return;

  const filteredData = examHistory.value.filter(
    (item) => item.subject === chartSubject.value
  );
  // 取最近5次，反转后最新在右边
  const recentData = filteredData.slice(0, 5).reverse();

  // 横轴用试题出处，兼容老数据（空则显示"未填写出处"），超过8字截断
  const xData = recentData.map((item) => {
    const src = item.questionSource;
    if (!src || !src.trim()) return "未填写出处";
    return src.length > 8 ? src.slice(0, 8) + "…" : src;
  });
  // tooltip 用完整出处
  const xDataFull = recentData.map((item) => {
    const src = item.questionSource;
    return !src || !src.trim() ? "未填写出处" : src;
  });

  const scoreData = recentData.map((item) => item.score);
  const durationData = recentData.map((item) => (item.durationSeconds / 60).toFixed(1));
  const maxScore = ["政治", "英语"].includes(chartSubject.value) ? 100 : 150;

  const tooltipFormatter = (params) => {
    const idx = params[0].dataIndex;
    const fullSrc = xDataFull[idx];
    return params.map((p) => `${fullSrc}<br/>${p.seriesName}: ${p.value}`).join("<br/>");
  };

  scoreChart.setOption({
    tooltip: { trigger: "axis", formatter: tooltipFormatter },
    grid: { top: 30, bottom: 40, left: 30, right: 20, containLabel: true },
    xAxis: { type: "category", data: xData, axisLabel: { interval: 0, rotate: 20, fontSize: 11 } },
    yAxis: { type: "value", min: 0, max: maxScore },
    series: [{
      name: "得分",
      data: scoreData,
      type: "line",
      smooth: true,
      areaStyle: {
        opacity: 0.3,
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "#67c23a" },
          { offset: 1, color: "#f0f9eb" },
        ]),
      },
      itemStyle: { color: "#67c23a" },
      lineStyle: { width: 3 },
    }],
  });

  timeChart.setOption({
    tooltip: { trigger: "axis", formatter: tooltipFormatter },
    grid: { top: 30, bottom: 40, left: 30, right: 20, containLabel: true },
    xAxis: { type: "category", data: xData, axisLabel: { interval: 0, rotate: 20, fontSize: 11 } },
    yAxis: { type: "value", name: "分钟" },
    series: [{
      name: "用时",
      data: durationData,
      type: "line",
      smooth: true,
      areaStyle: {
        opacity: 0.3,
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "#409eff" },
          { offset: 1, color: "#ecf5ff" },
        ]),
      },
      itemStyle: { color: "#409eff" },
      lineStyle: { width: 3 },
    }],
  });
};

const initCharts = () => {
  if (scoreChartRef.value && timeChartRef.value) {
    scoreChart = echarts.init(scoreChartRef.value);
    timeChart = echarts.init(timeChartRef.value);
    const commonOption = {
      xAxis: { type: "category", data: [] },
      yAxis: { type: "value" },
      series: [],
    };
    scoreChart.setOption(commonOption);
    timeChart.setOption(commonOption);
    window.addEventListener("resize", () => {
      scoreChart.resize();
      timeChart.resize();
    });
  }
};

// ================== 考试逻辑 ==================
const examPageRef = ref(null);
const isFullscreen = ref(false);

const toggleFullscreen = () => {
  if (!isFullscreen.value) {
    examPageRef.value?.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
};

const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement;
  if (data.isStarted && !isFullscreen.value && !data.isFinished) {
    ElMessage.warning("考试中请勿退出全屏模式！");
    speak("考试中请勿退出全屏模式！");
  }
};

const speak = (text) => {
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = "zh-CN";
  window.speechSynthesis.speak(utter);
};

const startExam = async () => {
  await examPageRef.value?.requestFullscreen();
  data.isStarted = true;
  data.isFinished = false;
  data.startTime = new Date();
  data.totalDuration = examMode.value;
  data.remainingSeconds = examMode.value;

  speak("考试开始，请同学们开始答题！");

  data.timer = setInterval(() => {
    if (data.remainingSeconds > 0) {
      data.remainingSeconds--;
      if (data.remainingSeconds === 1800) speak("距离考试结束还有半小时，请抓紧时间！");
      if (data.remainingSeconds === 0) finishExam(true);
    }
  }, 1000);
};

const finishExam = (auto = false) => {
  if (!data.isStarted) return;
  clearInterval(data.timer);
  data.isFinished = true;
  data.endTime = new Date();

  const durationSeconds = Math.floor(
    (data.endTime.getTime() - data.startTime.getTime()) / 1000
  );
  const hours = Math.floor(durationSeconds / 3600);
  const minutes = Math.floor((durationSeconds % 3600) / 60);
  const seconds = Math.floor(durationSeconds % 60);
  data.durationText = `${hours}小时${minutes}分${seconds}秒`;
  data.durationSeconds = durationSeconds;

  if (document.fullscreenElement) document.exitFullscreen();

  if (auto) {
    speak("考试结束，请停止答题！");
    ElMessage.info("考试时间已到，自动交卷");
  } else {
    speak("答题已完成，请填写考试成绩！");
    ElMessage.success("请填写考试成绩");
  }
  dialogVisible.value = true;
};

const submitResult = () => {
  if (!formData.subject) {
    ElMessage.warning("请选择考试科目！");
    return;
  }
  if (!formData.questionSource || !formData.questionSource.trim()) {
    ElMessage.warning("请填写试题出处！");
    return;
  }
  if (formData.score === null || formData.score === "") {
    ElMessage.warning("请填写考试成绩！");
    return;
  }

  // 根据 examMode 自动生成模拟模式，不让用户手填
  const simulationMode = examMode.value === 10800 ? "标准模式" : "演示模式";

  request
    .post("/exam/saveResult", {
      subject: formData.subject,
      questionSource: formData.questionSource,
      score: formData.score,
      duration: data.durationSeconds,
      simulationMode,
    })
    .then((res) => {
      if (res.code === "200") {
        ElMessage.success("考试结果提交成功！");
        dialogVisible.value = false;
        loadExamHistory();

        data.isStarted = false;
        data.isFinished = false;
        data.startTime = null;
        data.endTime = null;
        data.remainingSeconds = examMode.value;
        data.durationText = "";
        formData.subject = "";
        formData.questionSource = "";
        formData.score = null;
      } else {
        ElMessage.error(res.msg || "提交失败");
      }
    });
};

// ================== 生命周期 ==================
onMounted(() => {
  document.addEventListener("fullscreenchange", handleFullscreenChange);
  nextTick(() => {
    initCharts();
    loadExamHistory();
  });
});

onUnmounted(() => {
  if (data.timer) clearInterval(data.timer);
  document.removeEventListener("fullscreenchange", handleFullscreenChange);
  window.removeEventListener("resize", () => {
    scoreChart?.resize();
    timeChart?.resize();
  });
});
</script>

<style scoped>
.exam-page {
  position: fixed;
  top: 60px;
  left: 0;
  width: 100vw;
  height: calc(100vh - 60px);
  display: flex;
  justify-content: center;
  align-items: center;
  background-image: url("@/assets/imgs/考场.png");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-color: rgba(255, 255, 255, 0.3);
  background-blend-mode: overlay;
  overflow: hidden;
  z-index: 10;
  margin: 0;
  padding: 0;
}

.content-wrapper {
  display: flex;
  width: 90%;
  max-width: 1500px;
  height: 85vh;
  gap: 30px;
}

.dashboard-panel {
  width: 420px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.panel-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #333;
}

/* 近五次 / 全部 切换 */
.view-tabs {
  display: flex;
  gap: 4px;
  background: #f0f2f5;
  border-radius: 20px;
  padding: 3px;
}
.view-tab {
  padding: 4px 12px;
  border-radius: 16px;
  cursor: pointer;
  font-size: 13px;
  color: #666;
  transition: all 0.2s;
  white-space: nowrap;
}
.view-tab.active {
  background: #67c23a;
  color: white;
  box-shadow: 0 2px 6px rgba(103, 194, 58, 0.3);
}
.view-tab:not(.active):hover {
  background: rgba(103, 194, 58, 0.15);
  color: #67c23a;
}

.subject-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.tab-item {
  padding: 6px 12px;
  background: #f0f2f5;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  color: #666;
  transition: all 0.3s;
}
.tab-item:hover,
.tab-item.active {
  background: #67c23a;
  color: white;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
}

.chart-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow-y: hidden;
}

.chart-box {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  padding: 15px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  flex: 1;
}
.chart-box h4 {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #555;
  flex-shrink: 0;
}
.chart {
  flex: 1;
  width: 100%;
  min-height: 200px;
}

.exam-panel {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.exam-container {
  width: 100%;
  max-width: 800px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  padding: 50px;
  text-align: center;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.6);
  position: relative;
}

.exam-header {
  margin-bottom: 30px;
}

.timer-display {
  font-size: 100px;
  font-weight: 800;
  color: #67c23a;
  font-family: "Courier New", monospace;
  letter-spacing: 4px;
  text-shadow: 0 2px 10px rgba(103, 194, 58, 0.3);
  margin-bottom: 10px;
  transition: color 0.3s;
}
.timer-display.time-warning {
  color: #f56c6c;
  text-shadow: 0 2px 10px rgba(245, 108, 108, 0.3);
}

.exam-status-text {
  font-size: 16px;
  color: #888;
  margin-bottom: 30px;
}
.exam-status-text.finished {
  color: #f56c6c;
  font-weight: bold;
}

.progress-bar {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  margin: 0 auto 40px;
  width: 80%;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: #67c23a;
  transition: width 1s linear;
}
.progress-fill.warning {
  background: #f56c6c;
}

.exam-buttons {
  display: flex;
  justify-content: center;
  gap: 25px;
  margin-bottom: 30px;
}

.action-btn {
  font-weight: bold;
  padding: 24px 32px;
  font-size: 16px;
  border-radius: 12px;
  transition: transform 0.2s;
}
.action-btn:active {
  transform: scale(0.95);
}
.start-btn {
  box-shadow: 0 4px 15px rgba(103, 194, 58, 0.4);
}
.stop-btn {
  box-shadow: 0 4px 15px rgba(144, 147, 153, 0.4);
}
.screen-btn {
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.4);
}

.footer-tip {
  color: #909399;
  font-size: 14px;
  margin-top: 20px;
}

.result-summary {
  font-size: 18px;
  color: #333;
  margin-top: 20px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
}
.result-summary span {
  font-weight: bold;
  color: #409eff;
}
</style>
