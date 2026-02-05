<template>
  <div class="main-content exam-page" ref="examPageRef">
    <div class="exam-container">
      <div v-if="data.isStarted && !data.isFinished" class="exam-summary">
        <h2>✅ 正在考试</h2>
      </div>

      <div v-if="data.isFinished" class="exam-summary">
        <h2>✅ 考试已结束</h2>
      </div>

      <div class="exam-time">{{ formattedTime }}</div>

      <div class="exam-buttons">
        <el-button
          type="success"
          size="large"
          :disabled="data.isStarted && !data.isFinished"
          @click="startExam"
        >
          开始答题
        </el-button>

        <el-button
          type="danger"
          size="large"
          :disabled="!data.isStarted || data.isFinished"
          @click="finishExam"
        >
          完成答题
        </el-button>

        <!-- ✅ 可选：手动切换全屏 -->
        <el-button type="primary" size="large" @click="toggleFullscreen">
          {{ isFullscreen ? "退出全屏" : "进入全屏" }}
        </el-button>
      </div>

      <div v-if="data.isFinished" class="exam-summary">
        <p>您的答题时间为：{{ data.durationText }}</p>
      </div>
    </div>

    <!-- ✅ 弹出输入框 -->
    <el-dialog
      title="考试结果提交"
      v-model="dialogVisible"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="80px">
        <el-form-item label="考试科目">
          <el-select
            v-model="formData.subject"
            placeholder="请选择考试科目"
            style="width: 100%"
          >
            <el-option label="政治" value="政治" />
            <el-option label="英语" value="英语" />
            <el-option label="数学" value="数学" />
            <el-option label="专业课" value="专业课" />
          </el-select>
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
        <el-button type="primary" @click="submitResult">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, computed, ref, onMounted, onUnmounted } from "vue";
import { ElMessage } from "element-plus";
import request from "@/utils/request";

// ================== 时间格式化函数 ==================
const formatTime = (hours, minutes, seconds) => {
  return `${hours.toString().padStart(2, "0")}:${minutes
    .toString()
    .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
};

// ================== 响应式状态 ==================
const data = reactive({
  isStarted: false,
  isFinished: false,
  startTime: null,
  endTime: null,
  remainingSeconds: 3 * 60 * 60, // 三小时
  timer: null,
  durationText: "",
});

const dialogVisible = ref(false);
const formData = reactive({
  subject: "",
  score: null,
});

// ================== 计算属性 ==================
const formattedTime = computed(() => {
  const h = Math.floor(data.remainingSeconds / 3600);
  const m = Math.floor((data.remainingSeconds % 3600) / 60);
  const s = data.remainingSeconds % 60;
  return formatTime(h, m, s);
});

// ================== 全屏相关 ==================
const examPageRef = ref(null);
const isFullscreen = ref(false);

// 切换全屏模式
const toggleFullscreen = () => {
  if (!isFullscreen.value) {
    examPageRef.value?.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
};

// 监听全屏状态变化
const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement;

  // 如果考试中退出全屏，可提示用户
  if (data.isStarted && !isFullscreen.value && !data.isFinished) {
    ElMessage.warning("考试中请勿退出全屏模式！");
    speak("考试中请勿退出全屏模式！");
  }
};

// ================== 语音播报 ==================
const speak = (text) => {
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = "zh-CN";
  window.speechSynthesis.speak(utter);
};

// ================== 开始考试 ==================
const startExam = async () => {
  // 自动进入全屏
  await examPageRef.value?.requestFullscreen();

  data.isStarted = true;
  data.isFinished = false;
  data.startTime = new Date();
  data.remainingSeconds = 3 * 60 * 60;
  speak("考试开始，请同学们开始答题！");

  data.timer = setInterval(() => {
    if (data.remainingSeconds > 0) {
      data.remainingSeconds--;

      if (data.remainingSeconds === 30 * 60) {
        speak("距离考试结束还有半小时，请抓紧时间！");
      }

      if (data.remainingSeconds === 0) {
        finishExam(true);
      }
    }
  }, 1000);
};

// ================== 完成考试 ==================
const finishExam = (auto = false) => {
  if (!data.isStarted) return;
  clearInterval(data.timer);
  data.isFinished = true;
  data.endTime = new Date();

  const durationSeconds =
    (data.endTime.getTime() - data.startTime.getTime()) / 1000;
  const hours = Math.floor(durationSeconds / 3600);
  const minutes = Math.floor((durationSeconds % 3600) / 60);
  const seconds = Math.floor(durationSeconds % 60);
  data.durationText = `${hours}小时${minutes}分${seconds}秒`;
  data.durationSeconds = durationSeconds;

  // 退出全屏
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

// ================== 提交成绩 ==================
const submitResult = () => {
  if (!formData.subject || formData.score === null) {
    ElMessage.warning("请填写完整的考试科目和成绩！");
    return;
  }

  request
    .post("/exam/saveResult", {
      subject: formData.subject,
      score: formData.score,
      duration: data.durationSeconds,
    })
    .then((res) => {
      if (res.code === "200") {
        ElMessage.success("考试结果提交成功！");
        dialogVisible.value = false;

        // ✅ 重置所有状态
        data.isStarted = false;
        data.isFinished = false;
        data.startTime = null;
        data.endTime = null;
        data.remainingSeconds = 3 * 60 * 60;
        data.durationText = "";
        formData.subject = "";
        formData.score = null;
      } else {
        ElMessage.error(res.msg || "提交失败");
      }
    });
};

// ================== 生命周期 ==================
onMounted(() => {
  document.addEventListener("fullscreenchange", handleFullscreenChange);
});

onUnmounted(() => {
  if (data.timer) clearInterval(data.timer);
  document.removeEventListener("fullscreenchange", handleFullscreenChange);
});
</script>

<style scoped>
.exam-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-image: url("@/assets/imgs/考场.png");
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  background-color: rgba(255, 255, 255, 0.3);
  background-blend-mode: overlay;
}

.exam-container {
  background: rgba(255, 255, 255, 0.75);
  padding: 60px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  text-align: center;
  backdrop-filter: blur(5px);
}

.exam-time {
  font-size: 80px;
  font-weight: bold;
  color: #49c48d;
  margin-bottom: 40px;
  font-family: "Courier New", monospace;
}

.exam-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.exam-summary {
  margin-top: 0px;
  font-size: 20px;
  color: #333;
}
</style>
