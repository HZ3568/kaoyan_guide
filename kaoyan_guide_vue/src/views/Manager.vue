<template>
  <div class="manager-container">
    <div class="manager-header">
      <div class="manager-header-left">
        <img
          src="@/assets/imgs/logo.png"
          alt=""
        />
        <div class="title">研途规划</div>
      </div>
      <div class="manager-header-center">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/manager/home' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>{{
            router.currentRoute.value.meta.name
          }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="manager-header-right">
        <el-dropdown style="cursor: pointer">
          <div class="manager-user">
            <img
              style="width: 40px; height: 40px; border-radius: 50%"
              :src="data.user.avatar || defaultAvatar"
              @error="handleAvatarError"
              alt=""
            />
            <span class="manager-user__name">{{
              data.user.name
            }}</span><el-icon><arrow-down /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="router.push('/manager/person')">个人资料</el-dropdown-item>
              <el-dropdown-item @click="router.push('/manager/password')">修改密码</el-dropdown-item>
              <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    <!-- 下面部分开始 -->
    <div class="manager-body">
      <div class="manager-main-left">
        <el-menu
          :default-active="router.currentRoute.value.path"
          :default-openeds="['1', '2']"
          router
        >
          <el-menu-item index="/manager/home">
            <el-icon>
              <HomeFilled />
            </el-icon>
            <span>系统首页</span>
          </el-menu-item>
          <el-menu-item
            index="/manager/dataStatistics"
            v-if="data.user.role === 'ADMIN'"
          >
            <el-icon>
              <Histogram />
            </el-icon>
            <span>数据统计</span>
          </el-menu-item>

          <!-- 院校信息管理 -->
          <el-sub-menu
            index="school"
            v-if="data.user.role === 'ADMIN'"
          >
            <template #title>
              <el-icon>
                <School />
              </el-icon>
              <span>院校信息管理</span>
            </template>
            <el-menu-item index="/manager/school/university">学校信息</el-menu-item>
            <el-menu-item index="/manager/school/areas">地区信息</el-menu-item>
            <el-menu-item index="/manager/school/categorys">门类信息</el-menu-item>
            <el-menu-item index="/manager/school/specialtys">专业信息</el-menu-item>
            <el-menu-item index="/manager/school/interpretations">专业解读</el-menu-item>
            <el-menu-item index="/manager/school/policys">招生政策</el-menu-item>
            <el-menu-item index="/manager/school/comment">院校评价</el-menu-item>
            <el-menu-item index="/manager/school/universitySpecialtys">学校专业</el-menu-item>
          </el-sub-menu>

          <!-- 智能服务管理 -->
          <el-sub-menu
            index="ai"
            v-if="data.user.role === 'ADMIN'"
          >
            <template #title>
              <el-icon>
                <Cpu />
              </el-icon>
              <span>智能服务管理</span>
            </template>
            <el-menu-item index="/manager/ai/knowledgeBase">知识库管理</el-menu-item>
            <el-menu-item index="/manager/ai/consultSession">咨询会话管理</el-menu-item>
            <el-menu-item index="/manager/ai/studyPlan">学习规划管理</el-menu-item>
          </el-sub-menu>

          <!-- 考场模拟管理 -->
          <el-sub-menu
            index="exam"
            v-if="data.user.role === 'ADMIN'"
          >
            <template #title>
              <el-icon>
                <Document />
              </el-icon>
              <span>考场模拟管理</span>
            </template>
            <el-menu-item index="/manager/exam/question">题库管理</el-menu-item>
            <el-menu-item index="/manager/exam/examData">考试数据管理</el-menu-item>
          </el-sub-menu>

          <!-- 用户管理 -->
          <el-sub-menu
            index="user"
            v-if="data.user.role === 'ADMIN'"
          >
            <template #title>
              <el-icon>
                <UserFilled />
              </el-icon>
              <span>用户管理</span>
            </template>
            <el-menu-item index="/manager/user/admin">管理员信息</el-menu-item>
            <el-menu-item index="/manager/user/user">学生信息</el-menu-item>
          </el-sub-menu>

          <!-- 系统内容管理 -->
          <el-sub-menu
            index="system"
            v-if="data.user.role === 'ADMIN'"
          >
            <template #title>
              <el-icon>
                <Setting />
              </el-icon>
              <span>系统内容管理</span>
            </template>
            <el-menu-item index="/manager/system/slideshow">轮播图管理</el-menu-item>
            <el-menu-item index="/manager/system/notice">系统公告</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </div>
      <div class="manager-main-right">
        <RouterView @updateUser="updateUser" />
      </div>
    </div>
    <!-- 下面部分结束 -->
  </div>
</template>

<script setup>
import { reactive } from "vue";
import router from "@/router/index.js";
import { ElMessage } from "element-plus";
import defaultAvatar from "@/assets/imgs/avatar.png";

const data = reactive({
  user: JSON.parse(localStorage.getItem("xm-admin") || "{}"),
});

const logout = () => {
  localStorage.removeItem("xm-admin");
  router.push("/login");
};

const updateUser = () => {
  data.user = JSON.parse(localStorage.getItem("xm-admin") || "{}");
};

const handleAvatarError = (event) => {
  event.target.src = defaultAvatar;
};

if (!data.user.id) {
  logout();
  ElMessage.error("请登录！");
}
</script>

<style scoped>
@import "@/assets/css/manager.css";
</style>
