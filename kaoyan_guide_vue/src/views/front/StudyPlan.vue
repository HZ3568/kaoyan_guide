<template>
  <div class="main-content">
    <!-- 顶部 Header -->
    <div class="header-container">
      <div class="header-left">
        <el-icon :size="24" color="#5B50E7"><Notebook /></el-icon>
        <div class="title-wrapper">
          <span class="main-title">考研智能伴学系统</span>
          <span class="sub-title">你的私人 AI 考研规划师</span>
        </div>
      </div>
      <div class="header-right">
        <div class="countdown-pill">
          <el-icon :size="16" color="#5B50E7"><Clock /></el-icon>
          <span class="countdown-text"
            >距离 2027 考研还有
            <span class="countdown-num">{{ daysLeft }}</span> 天</span
          >
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- 左侧区域 -->
      <div class="left-panel">
        <!-- 日历卡片 -->
        <div class="panel-card calendar-card">
          <el-calendar v-model="currentDate" ref="calendar">
            <template #date-cell="{ data }">
              <div
                class="calendar-cell"
                :class="{
                  'is-selected': isSelected(data.day),
                  'is-today': isToday(data.day),
                }"
                @click="handleDateClick(data.day)"
              >
                <div class="date-num">
                  {{ data.day.split("-").slice(2).join("") }}
                </div>
                <!-- 如果有计划，显示小绿点 -->
                <div v-if="hasPlan(data.day)" class="plan-dot"></div>
              </div>
            </template>
          </el-calendar>
        </div>

        <!-- 进度卡片 -->
        <div class="panel-card progress-card">
          <div class="card-title">当日进度概览</div>
          <div class="progress-content">
            <div class="progress-info">
              <div class="info-label">已完成任务</div>
              <div class="info-num">
                {{ completedCount }}<span class="unit">个</span>
              </div>
            </div>
            <div class="progress-chart">
              <el-progress
                type="circle"
                :percentage="completionPercentage"
                :width="70"
                color="#5B50E7"
                :stroke-width="6"
              >
                <template #default="{ percentage }">
                  <span class="percentage-value">{{ percentage }}%</span>
                </template>
              </el-progress>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧区域 -->
      <div class="right-panel">
        <div class="panel-card detail-card" v-loading="loading">
          <div class="detail-header">
            <div class="header-date">
              <el-icon :size="22" color="#333"><CalendarIcon /></el-icon>
              <span class="date-text"
                >{{ formatDateCN(selectedDate) }} 规划</span
              >
            </div>
            <div class="header-weekday">{{ getWeekday(selectedDate) }}</div>
          </div>

          <!-- 场景A：今日无计划，且选中的是今天 -->
          <div v-if="!currentPlan && isSelectedToday" class="generate-section">
            <div class="empty-placeholder">
              <div class="empty-text">
                今天还没有生成学习规划哦，快来制定吧！
              </div>
            </div>

            <div class="input-area">
              <div class="input-label">
                <el-icon><EditPen /></el-icon> 昨天的学习状态 / 今日心情
              </div>
              <el-input
                type="textarea"
                :rows="4"
                placeholder="例如：昨天完成了高数第二章习题，感觉对极限的概念理解加深了..."
                v-model="feedback"
                maxlength="200"
                show-word-limit
                class="custom-textarea"
              ></el-input>
            </div>

            <div class="action-area">
              <el-button
                type="primary"
                class="generate-btn"
                @click="generatePlan"
                :loading="generating"
                round
              >
                生成今日专属规划
                <el-icon class="el-icon--right"><MagicStick /></el-icon>
              </el-button>
            </div>
          </div>

          <!-- 场景B：已有计划 -->
          <div v-else-if="currentPlan" class="plan-content">
            <!-- 顶部操作栏：仅当天可撤回 -->
            <div class="plan-actions" v-if="isSelectedToday">
              <el-button
                type="danger"
                plain
                size="small"
                @click="withdrawPlan"
                class="withdraw-btn"
              >
                <el-icon style="margin-right: 4px"><RefreshLeft /></el-icon>
                撤回今日计划
              </el-button>
            </div>

            <!-- 状态反馈 -->
            <div class="section-block">
              <div class="section-header">
                <el-icon color="#5B50E7"><Connection /></el-icon>
                <span>你的状态反馈</span>
              </div>
              <div class="feedback-display">
                "{{ currentPlan.userFeedback || "无" }}"
              </div>
            </div>

            <!-- AI 建议 -->
            <div class="section-block">
              <div class="section-header">
                <el-icon color="#5B50E7"><ChatLineRound /></el-icon>
                <span>AI 导师建议</span>
              </div>
              <div class="advice-display">
                {{ currentPlan.aiAdvice }}
              </div>
            </div>

            <!-- 任务清单 -->
            <div class="section-block">
              <div class="section-header">
                <el-icon color="#5B50E7"><CircleCheck /></el-icon>
                <span>专属任务清单</span>
              </div>
              <div class="task-list-container">
                <div
                  v-for="(task, index) in taskList"
                  :key="index"
                  class="task-card"
                  @click="toggleTask(index)"
                  :class="{ 'is-completed': task.completed }"
                >
                  <div class="task-left">
                    <div class="task-checkbox-wrapper">
                      <div
                        class="custom-checkbox"
                        :class="{ checked: task.completed }"
                      >
                        <el-icon v-if="task.completed" color="#fff" :size="12"
                          ><Check
                        /></el-icon>
                      </div>
                    </div>
                    <div class="task-main">
                      <el-tag
                        :type="getTagType(task.subject)"
                        effect="light"
                        size="small"
                        class="task-tag"
                        >{{ task.subject }}</el-tag
                      >
                      <div
                        class="task-desc"
                        :class="{ 'text-through': task.completed }"
                      >
                        {{ task.content }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 场景C：无计划且不是今天 -->
          <div v-else class="no-plan-empty">
            <el-empty
              description="该日期没有学习规划记录"
              :image-size="120"
            ></el-empty>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Calendar as CalendarIcon,
  Notebook,
  Clock,
  EditPen,
  MagicStick,
  Connection,
  ChatLineRound,
  CircleCheck,
  Check,
  RefreshLeft,
} from "@element-plus/icons-vue";
import request from "@/utils/request";

const currentDate = ref(new Date());
const calendar = ref(null);
const selectedDate = ref(new Date());
const currentPlan = ref(null);
const feedback = ref("");
const loading = ref(false);
const generating = ref(false);
const daysLeft = ref(0);
let timer = null;

// 倒计时逻辑
const updateCountdown = () => {
  const now = new Date();
  const target = new Date("2026-12-25T00:00:00");
  const diff = target - now;
  if (diff > 0) {
    daysLeft.value = Math.ceil(diff / (1000 * 60 * 60 * 24));
  } else {
    daysLeft.value = 0;
  }
};

// 格式化日期：2026-03-05
const formatDate = (date) => {
  if (!date) return "";
  const y = date.getFullYear();
  const m = (date.getMonth() + 1).toString().padStart(2, "0");
  const d = date.getDate().toString().padStart(2, "0");
  return `${y}-${m}-${d}`;
};

// 格式化日期中文：2026年03月05日
const formatDateCN = (date) => {
  if (!date) return "";
  const y = date.getFullYear();
  const m = (date.getMonth() + 1).toString().padStart(2, "0");
  const d = date.getDate().toString().padStart(2, "0");
  return `${y}年${m}月${d}日`;
};

// 获取星期
const getWeekday = (date) => {
  if (!date) return "";
  const days = [
    "星期日",
    "星期一",
    "星期二",
    "星期三",
    "星期四",
    "星期五",
    "星期六",
  ];
  return days[date.getDay()];
};

const isSelectedToday = computed(() => {
  return formatDate(selectedDate.value) === formatDate(new Date());
});

const isToday = (dayStr) => {
  return dayStr === formatDate(new Date());
};

const isSelected = (dayStr) => {
  return dayStr === formatDate(selectedDate.value);
};

const hasPlan = (date) => {
  // TODO: 后续对接实际数据
  return false;
};

const handleDateClick = (date) => {
  selectedDate.value = new Date(date);
  fetchPlan(formatDate(selectedDate.value));
};

const fetchPlan = (dateStr) => {
  loading.value = true;
  request
    .get("/study-plan/" + dateStr)
    .then((res) => {
      if (res.code === "200" && res.data) {
        currentPlan.value = res.data;
      } else {
        currentPlan.value = null;
      }
    })
    .catch(() => {
      currentPlan.value = null;
    })
    .finally(() => {
      loading.value = false;
    });
};

const generatePlan = () => {
  if (!feedback.value.trim()) {
    ElMessage.warning("请填写昨天的反馈或今日心情哦~");
    return;
  }
  generating.value = true;
  request
    .post("/study-plan/generate", { feedback: feedback.value })
    .then((res) => {
      if (res.code === "200") {
        ElMessage.success("生成成功！加油！");
        currentPlan.value = res.data;
      } else {
        ElMessage.error(res.msg || "生成失败");
      }
    })
    .catch((err) => {
      ElMessage.error("生成失败，请稍后重试");
    })
    .finally(() => {
      generating.value = false;
    });
};

const withdrawPlan = () => {
  ElMessageBox.confirm(
    "撤回后将删除今日生成的计划记录，并返回到生成前的状态，确定要撤回吗？",
    "确认撤回",
    {
      confirmButtonText: "确定撤回",
      cancelButtonText: "取消",
      type: "warning",
    }
  )
    .then(() => {
      loading.value = true;
      request
        .delete("/study-plan/" + formatDate(selectedDate.value))
        .then((res) => {
          if (res.code === "200") {
            ElMessage.success("撤回成功");
            currentPlan.value = null;
            // 重新获取一下（虽然已经置空，但为了保险起见，或者直接置空即可）
            // fetchPlan(formatDate(selectedDate.value)); // 不需要，因为已经置空了
          } else {
            ElMessage.error(res.msg || "撤回失败");
          }
        })
        .finally(() => {
          loading.value = false;
        });
    })
    .catch(() => {});
};

const parseTasks = (tasks) => {
  if (!tasks) return [];
  if (typeof tasks === "string") {
    try {
      return JSON.parse(tasks);
    } catch (e) {
      console.error("JSON parse error", e);
      return [];
    }
  }
  return tasks;
};

const getTagType = (subject) => {
  if (subject && subject.includes("数学")) return "primary";
  if (subject && subject.includes("英语")) return "warning";
  if (subject && subject.includes("政治")) return "danger";
  return "success";
};

const taskList = ref([]);

const completedCount = computed(() => {
  return taskList.value.filter((t) => t.completed).length;
});

const totalTasks = computed(() => {
  return taskList.value.length;
});

const completionPercentage = computed(() => {
  if (totalTasks.value === 0) return 0;
  return Math.round((completedCount.value / totalTasks.value) * 100);
});

const toggleTask = (index) => {
  if (taskList.value[index]) {
    taskList.value[index].completed = !taskList.value[index].completed;
  }
};

watch(
  currentPlan,
  (newVal) => {
    if (newVal && newVal.dailyTasks) {
      let tasks = parseTasks(newVal.dailyTasks);
      // Ensure tasks is an array
      if (!Array.isArray(tasks)) {
        tasks = [];
      }
      // Initialize completed status if not present
      taskList.value = tasks.map((t) => ({
        ...t,
        completed: t.completed || false,
      }));
    } else {
      taskList.value = [];
    }
  },
  { immediate: true }
);

onMounted(() => {
  fetchPlan(formatDate(new Date()));
  updateCountdown();
  // 每秒检查一次日期变更，实际上不需要太频繁，分钟级即可，但为了秒级响应0点变更
  timer = setInterval(updateCountdown, 1000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
/* 全局布局 */
.main-content {
  padding: 20px 40px;
  background-color: #f5f7fa; /* 浅灰背景 */
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}

/* Header */
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.title-wrapper {
  display: flex;
  flex-direction: column;
}
.main-title {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  line-height: 1.2;
  color: #5b50e7; /* 品牌色 */
}
.sub-title {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
.header-right {
  display: flex;
  align-items: center;
}
.countdown-pill {
  background: #fff;
  padding: 8px 20px;
  border-radius: 50px;
  box-shadow: 0 2px 10px rgba(91, 80, 231, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}
.countdown-num {
  font-size: 20px;
  font-weight: 700;
  color: #5b50e7;
  margin: 0 4px;
}

/* 左右分栏 */
.content-wrapper {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}
.left-panel {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.right-panel {
  flex: 1;
  min-width: 0;
}

/* 卡片通用样式 */
.panel-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  overflow: hidden;
}

/* 日历样式覆盖 */
.calendar-card {
  padding: 20px;
}
:deep(.el-calendar) {
  --el-calendar-border: none;
  background: transparent;
}
:deep(.el-calendar__header) {
  padding: 0 0 20px 0;
  border-bottom: none;
}
:deep(.el-calendar__title) {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}
:deep(.el-calendar__body) {
  padding: 0;
}
:deep(.el-calendar-table) {
  border: none;
}
:deep(.el-calendar-table thead th) {
  color: #999;
  font-weight: normal;
  border: none;
  padding: 12px 0;
}
:deep(.el-calendar-table td) {
  border: none;
  padding: 0;
}
:deep(.el-calendar-table .el-calendar-day) {
  height: 48px;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}
:deep(.el-calendar-table td.is-selected) {
  background: transparent;
}
:deep(.el-calendar-table .el-calendar-day:hover) {
  background-color: transparent;
}

/* 日历单元格自定义 */
.calendar-cell {
  width: 36px;
  height: 36px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  position: relative;
  cursor: pointer;
  transition: all 0.2s;
  color: #666;
}
.calendar-cell:hover {
  background-color: #f0f0f5;
}
.calendar-cell.is-selected {
  background-color: #5b50e7;
  color: #fff;
  box-shadow: 0 4px 10px rgba(91, 80, 231, 0.3);
}
.date-num.is-today {
  color: #5b50e7;
  font-weight: 700;
}
.calendar-cell.is-selected .date-num.is-today {
  color: #fff;
}
.plan-dot {
  position: absolute;
  bottom: 4px;
  width: 4px;
  height: 4px;
  background: #00b578;
  border-radius: 50%;
}

/* 进度卡片 */
.progress-card {
  padding: 24px;
}
.card-title {
  font-size: 14px;
  color: #999;
  margin-bottom: 20px;
}
.progress-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fb;
  padding: 16px 20px;
  border-radius: 12px;
}
.info-label {
  font-size: 14px;
  color: #5b50e7;
  margin-bottom: 4px;
}
.info-num {
  font-size: 28px;
  font-weight: 700;
  color: #333;
}
.unit {
  font-size: 14px;
  font-weight: normal;
  color: #999;
  margin-left: 4px;
}
.percentage-value {
  font-size: 14px;
  font-weight: 700;
  color: #5b50e7;
}

/* 右侧详情 */
.detail-card {
  padding: 30px;
  min-height: 600px;
}
.detail-header {
  margin-bottom: 30px;
}
.header-date {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.date-text {
  font-size: 24px;
  font-weight: 800;
  color: #333;
}
.header-weekday {
  font-size: 14px;
  color: #999;
  margin-left: 32px;
}

/* 生成区域 */
.generate-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 40px;
}
.empty-text {
  color: #999;
  margin: 20px 0;
  font-size: 16px;
}
.input-area {
  width: 100%;
  max-width: 600px;
  margin-bottom: 30px;
}
.input-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}
.custom-textarea {
  font-size: 15px;
}
:deep(.el-textarea__inner) {
  border-radius: 12px;
  padding: 16px;
  background-color: #f8f9fb;
  border: 1px solid #eee;
  box-shadow: none;
}
:deep(.el-textarea__inner:focus) {
  background-color: #fff;
  border-color: #5b50e7;
}
.generate-btn {
  padding: 12px 40px;
  font-size: 16px;
  height: auto;
  background-color: #5b50e7;
  border-color: #5b50e7;
  box-shadow: 0 6px 16px rgba(91, 80, 231, 0.25);
}
.generate-btn:hover {
  background-color: #4a40d0;
  border-color: #4a40d0;
}

/* 详情内容区域 */
.plan-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
  position: relative;
}

.plan-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: -20px; /* 拉近与下方内容的距离 */
}

.withdraw-btn {
  border-radius: 8px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #333;
  margin-bottom: 16px;
}
.feedback-display {
  background: #f8f9fb;
  padding: 20px;
  border-radius: 12px;
  color: #666;
  font-style: italic;
  font-size: 15px;
  line-height: 1.6;
}
.advice-display {
  background: #ebf5ff;
  padding: 20px;
  border-radius: 12px;
  color: #2d5bff;
  font-size: 15px;
  line-height: 1.7;
  border: 1px solid rgba(45, 91, 255, 0.1);
}

/* 任务列表 */
.task-list-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.task-card:hover {
  border-color: #5b50e7;
  box-shadow: 0 4px 12px rgba(91, 80, 231, 0.08);
  transform: translateY(-2px);
}
.task-left {
  display: flex;
  gap: 16px;
  width: 100%;
}
.task-checkbox-wrapper {
  padding-top: 4px;
}
.custom-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid #ddd;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.2s;
}
.custom-checkbox.checked {
  background-color: #5b50e7;
  border-color: #5b50e7;
}
.task-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: flex-start;
  transition: all 0.2s;
  cursor: pointer;
}
.task-card.is-completed {
  background-color: #f8f9fb;
  border-color: transparent;
}
.task-desc.text-through {
  text-decoration: line-through;
  color: #999;
}
.task-main {
  flex: 1;
}
.task-tag {
  margin-bottom: 8px;
  font-weight: 600;
  border-radius: 6px;
}
.task-desc {
  font-size: 15px;
  color: #333;
  line-height: 1.5;
}
.no-plan-empty {
  padding-top: 60px;
}
</style>
