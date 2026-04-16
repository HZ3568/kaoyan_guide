<template>
  <div class="register-container">
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

    <!-- 右侧注册区 -->
    <div class="form-side">
      <div class="register-box">
        <div class="register-header">
          <h1 class="main-title">欢迎注册</h1>
          <p class="sub-title">开启你的备考之旅</p>
        </div>
        <div class="register-card">
          <el-form ref="formRef" :model="data.form" :rules="data.rules" autocomplete="off" @keydown.enter.prevent="register">
            <el-form-item prop="username">
              <el-input :prefix-icon="User" size="large" v-model="data.form.username" placeholder="请输入账号" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item prop="password">
              <el-input show-password :prefix-icon="Lock" size="large" v-model="data.form.password" placeholder="请输入密码" autocomplete="new-password"></el-input>
            </el-form-item>
            <el-form-item prop="confirmPassword">
              <el-input show-password :prefix-icon="Lock" size="large" v-model="data.form.confirmPassword" placeholder="请确认密码" autocomplete="new-password"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button size="large" type="primary" style="width: 100%; font-weight: 600; letter-spacing: 2px" @click="register">注 册</el-button>
            </el-form-item>
            <div style="text-align: center; font-size: 14px; color: rgba(47, 58, 51, 0.6)">
              已有账号？<router-link to="/login" style="color: #7fc8a9; font-weight: 600">立即登录</router-link>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { User, Lock } from "@element-plus/icons-vue";
import request from "@/utils/request.js";
import { ElMessage } from "element-plus";
import router from "@/router/index.js";

const validatePass = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else {
    if (value !== data.form.password) {
      callback(new Error("确认密码跟原密码不一致!"))
    }
    callback()
  }
}

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 5 || value.length > 18) {
    callback(new Error('密码必须为5-18位'))
  } else if (!/[a-zA-Z]/.test(value) || !/\d/.test(value)) {
    callback(new Error('密码必须同时包含字母和数字'))
  } else {
    callback()
  }
}

const data = reactive({
  form: {
    role: "USER"
  },
  rules: {
    username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
    password: [{ validator: validatePassword, trigger: 'blur' }],
    confirmPassword: [{ validator: validatePass, trigger: 'blur' }]
  }
})

const formRef = ref()

const register = () => {
  formRef.value.validate(valid => {
    if (valid) {
      request.post('/register', data.form).then(res => {
        if (res.code === '200') {
          ElMessage.success('注册成功，即将跳转到登录页')
          setTimeout(() => {
            router.push('/login')
          }, 1500)
        } else {
          ElMessage.error(res.msg)
        }
      })
    }
  })
}
</script>

<style scoped>
.register-container {
  display: flex;
  min-height: 100vh;
  background-color: #f8fbf8;
  overflow: hidden;
}

/* 左侧视觉区（与登录页保持一致） */
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

.abstract-scene {
  position: relative;
  width: 500px;
  height: 500px;
}

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

.card-line { height: 8px; background: #e6f4ea; border-radius: 4px; }
.line-1 { width: 80%; }
.line-2 { width: 100%; }
.line-3 { width: 60%; }

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

.particle {
  position: absolute;
  background: #a8d8b9;
  border-radius: 50%;
  opacity: 0.6;
}
.p1 { width: 15px; height: 15px; top: 20%; left: 30%; animation: float 7s ease-in-out infinite -2s; }
.p2 { width: 10px; height: 10px; bottom: 30%; right: 25%; animation: float 5s ease-in-out infinite -1s; }
.p3 { width: 8px; height: 8px; top: 40%; right: 20%; animation: float 8s ease-in-out infinite -3s; }

/* 右侧表单区 */
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

.register-box {
  width: 100%;
  max-width: 400px;
}

.register-header {
  margin-bottom: 40px;
  text-align: center;
}

.main-title {
  font-size: 26px;
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

.register-card {
  padding: 10px;
}

:deep(.el-input__wrapper) {
  background-color: #f8fbf8;
  border-radius: 12px;
  box-shadow: 0 0 0 1px #e6f4ea inset;
  padding: 8px 15px;
  transition: all 0.3s;
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

:deep(.el-select) {
  width: 100%;
}

/* 动画 */
@keyframes float {
  0%, 100% { transform: translate(-50%, -50%) rotate(-5deg) translateY(0); }
  50% { transform: translate(-50%, -50%) rotate(-5deg) translateY(-15px); }
}
@keyframes pulse {
  0%, 100% { opacity: 0.8; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.4; transform: translate(-50%, -50%) scale(1.1); }
}
@keyframes rotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

@media (max-width: 900px) {
  .visual-side { display: none; }
  .form-side {
    width: 100%;
    background: linear-gradient(135deg, #f8fbf8 0%, #eef7f1 100%);
  }
  .register-box {
    background: rgba(255, 255, 255, 0.9);
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(127, 200, 169, 0.15);
  }
}
</style>
