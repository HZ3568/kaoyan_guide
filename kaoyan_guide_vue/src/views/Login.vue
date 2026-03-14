<template>
  <div class="login-container">
    <!-- 左侧视觉区 -->
    <div class="visual-side">
      <div class="visual-content">
        <div class="abstract-scene">
          <div class="glow-bg"></div>
          <div class="floating-card">
            <div class="card-line line-1"></div>
            <div class="card-line line-2"></div>
            <div class="card-line line-3"></div>
          </div>
          <div class="orbit-circle"></div>
          <div class="floating-particles">
            <span class="particle p1"></span>
            <span class="particle p2"></span>
            <span class="particle p3"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录区 -->
    <div class="form-side">
      <div class="login-wrapper">
        <div class="login-header">
          <h1 class="main-title">考研学习规划与资源整合系统</h1>
          <p class="sub-title">让备考更高效、更清晰</p>
        </div>

        <div class="login-card">
          <el-form
            ref="formRef"
            :model="data.form"
            :rules="data.rules"
            class="login-form"
            @keydown.enter.prevent="login"
          >
            <el-form-item prop="username">
              <el-input
                v-model="data.form.username"
                :prefix-icon="User"
                placeholder="请输入账号"
                size="large"
                clearable
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="data.form.password"
                :prefix-icon="Lock"
                placeholder="请输入密码"
                show-password
                size="large"
              />
            </el-form-item>

            <el-form-item prop="role">
              <el-radio-group
                v-model="data.form.role"
                class="custom-radio-group"
              >
                <el-radio-button
                  v-for="role in roleOptions"
                  :key="role.value"
                  :label="role.value"
                >
                  {{ role.label }}
                </el-radio-button>
              </el-radio-group>
            </el-form-item>

            <div class="form-action">
              <el-button
                type="primary"
                class="submit-btn"
                :loading="loading"
                @click="login"
              >
                登录
              </el-button>
            </div>

            <div class="form-footer">
              <span>还没有账号？</span>
              <router-link to="/register">立即注册</router-link>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { Lock, User } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import router from "@/router/index.js";
import request from "@/utils/request.js";

const roleOptions = [
  { value: "USER", label: "学生" },
  { value: "ADMIN", label: "管理员" },
];

const data = reactive({
  form: {
    username: "",
    password: "",
    role: "USER",
  },
  rules: {
    username: [{ required: true, message: "请输入账号", trigger: "blur" }],
    password: [{ required: true, message: "请输入密码", trigger: "blur" }],
    role: [{ required: true, message: "请选择登录身份", trigger: "change" }],
  },
});

const formRef = ref();
const loading = ref(false);

const login = () => {
  if (loading.value) return;

  formRef.value.validate((valid) => {
    if (!valid) return;

    loading.value = true;

    request
      .post("/login", data.form)
      .then((res) => {
        if (res.code === "200") {
          ElMessage.success("登录成功");
          localStorage.setItem("xm-user", JSON.stringify(res.data));

          if (res.data.role === "USER") {
            router.push("/front/home");
          } else {
            router.push("/manager/home");
          }
        } else {
          ElMessage.error(res.msg);
        }
      })
      .catch(() => {
        ElMessage.error("登录失败，请稍后重试");
      })
      .finally(() => {
        loading.value = false;
      });
  });
};
</script>

<style scoped>
/* ---------------- 基础变量与布局 ---------------- */
:root {
  --primary-color: #7fc8a9;
  --primary-hover: #6bb392;
  --secondary-color: #a8d8b9;
  --accent-color: #e6f4ea;
  --bg-color: #f8fbf8;
  --text-main: #2f3a33;
  --text-sub: rgba(47, 58, 51, 0.6);
  --shadow-card: 0 10px 30px rgba(127, 200, 169, 0.15);
}

.login-container {
  display: flex;
  min-height: 100vh;
  background-color: #f8fbf8;
  overflow: hidden;
}

/* ---------------- 左侧视觉区 ---------------- */
.visual-side {
  width: 68%;
  position: relative;
  background: linear-gradient(135deg, #f8fbf8 0%, #eef7f1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.visual-content {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* 抽象动态场景 */
.abstract-scene {
  position: relative;
  width: 500px;
  height: 500px;
}

/* 背景光晕 */
.glow-bg {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #e6f4ea 0%, rgba(230, 244, 234, 0) 70%);
  border-radius: 50%;
  filter: blur(40px);
  animation: pulse 8s ease-in-out infinite;
}

/* 浮动卡片/书页 */
.floating-card {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 220px;
  height: 280px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #a8d8b9;
  border-radius: 20px;
  transform: translate(-50%, -50%) rotate(-5deg);
  box-shadow: 0 20px 40px rgba(127, 200, 169, 0.15);
  backdrop-filter: blur(10px);
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  animation: float 6s ease-in-out infinite;
}

.card-line {
  height: 8px;
  background: #e6f4ea;
  border-radius: 4px;
}
.line-1 {
  width: 80%;
}
.line-2 {
  width: 100%;
}
.line-3 {
  width: 60%;
}

/* 轨迹环 */
.orbit-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 360px;
  height: 360px;
  border: 1px dashed rgba(168, 216, 185, 0.5);
  border-radius: 50%;
  animation: rotate 20s linear infinite;
}

.orbit-circle::after {
  content: "";
  position: absolute;
  top: -6px;
  left: 50%;
  width: 12px;
  height: 12px;
  background: #7fc8a9;
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(127, 200, 169, 0.5);
}

/* 浮动粒子 */
.particle {
  position: absolute;
  background: #a8d8b9;
  border-radius: 50%;
  opacity: 0.6;
}

.p1 {
  width: 15px;
  height: 15px;
  top: 20%;
  left: 30%;
  animation: float 7s ease-in-out infinite -2s;
}
.p2 {
  width: 10px;
  height: 10px;
  bottom: 30%;
  right: 25%;
  animation: float 5s ease-in-out infinite -1s;
}
.p3 {
  width: 8px;
  height: 8px;
  top: 40%;
  right: 20%;
  animation: float 8s ease-in-out infinite -3s;
}

/* ---------------- 右侧表单区 ---------------- */
.form-side {
  width: 42%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #fff;
  position: relative;
  box-shadow: -10px 0 40px rgba(0, 0, 0, 0.02);
}

.login-wrapper {
  width: 100%;
  max-width: 400px;
}

.login-header {
  margin-bottom: 40px;
  text-align: center; /* 标题居中，也可改为 left */
}

.main-title {
  font-size: 28px;
  color: #2f3a33;
  font-weight: 600;
  margin: 0 0 10px 0;
  letter-spacing: 1px;
}

.sub-title {
  font-size: 14px;
  color: rgba(47, 58, 51, 0.5);
  margin: 0;
  letter-spacing: 2px;
}

.login-card {
  padding: 10px; /* 内部留白由 form item margin 撑开 */
}

/* Element Plus 样式覆盖 */
:deep(.el-input__wrapper) {
  background-color: #f8fbf8;
  border-radius: 12px;
  box-shadow: 0 0 0 1px #e6f4ea inset;
  padding: 8px 15px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #a8d8b9 inset;
  background-color: #fff;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #7fc8a9 inset, 0 0 0 3px rgba(127, 200, 169, 0.2);
  background-color: #fff;
}

:deep(.el-input__inner) {
  color: #2f3a33;
  height: 40px;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

/* Radio Group 样式 */
.custom-radio-group {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

:deep(.el-radio-button__inner) {
  width: 100%;
  border: 1px solid #e6f4ea;
  background: #f8fbf8;
  color: rgba(47, 58, 51, 0.7);
  border-radius: 12px !important;
  box-shadow: none !important;
  padding: 12px 0;
  transition: all 0.3s;
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #e6f4ea;
  border-color: #7fc8a9;
  color: #2f3a33;
  font-weight: 600;
}

:deep(.el-radio-button:first-child .el-radio-button__inner),
:deep(.el-radio-button:last-child .el-radio-button__inner) {
  border-radius: 12px;
}

/* 登录按钮 */
.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  border-radius: 12px;
  background-color: #7fc8a9;
  border: none;
  font-weight: 600;
  letter-spacing: 2px;
  transition: all 0.3s;
  box-shadow: 0 8px 16px rgba(127, 200, 169, 0.25);
}

.submit-btn:hover {
  background-color: #6bb392;
  transform: translateY(-2px);
  box-shadow: 0 12px 20px rgba(127, 200, 169, 0.3);
}

.submit-btn:active {
  transform: translateY(0);
}

.form-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: rgba(47, 58, 51, 0.6);
}

.form-footer a {
  color: #7fc8a9;
  text-decoration: none;
  font-weight: 600;
  margin-left: 5px;
}

.form-footer a:hover {
  text-decoration: underline;
}

/* ---------------- 动画定义 ---------------- */
@keyframes float {
  0%,
  100% {
    transform: translate(-50%, -50%) rotate(-5deg) translateY(0);
  }
  50% {
    transform: translate(-50%, -50%) rotate(-5deg) translateY(-15px);
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.8;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.4;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

@keyframes rotate {
  from {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  to {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}

/* ---------------- 响应式适配 ---------------- */
@media (max-width: 900px) {
  .visual-side {
    display: none;
  }
  .form-side {
    width: 100%;
    background: linear-gradient(135deg, #f8fbf8 0%, #eef7f1 100%);
  }
  .login-wrapper {
    background: rgba(255, 255, 255, 0.9);
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(127, 200, 169, 0.15);
  }
}
</style>
