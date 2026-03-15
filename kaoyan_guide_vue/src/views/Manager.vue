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
                :src="data.user.avatar"
                @error="handleAvatarError"
                alt=""
            />
            <span class="manager-user__name">{{
              data.user.name
            }}</span><el-icon><arrow-down /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                @click="router.push('/manager/person')"
              >个人资料</el-dropdown-item>
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
          <el-sub-menu
            index="1"
            v-if="data.user.role === 'ADMIN'"
          >
            <template #title>
              <el-icon>
                <Menu />
              </el-icon>
              <span>信息管理</span>
            </template>
            <el-menu-item
              index="/manager/areas"
              v-if="data.user.role === 'ADMIN'"
            >地区信息</el-menu-item>
            <el-menu-item
              index="/manager/categorys"
              v-if="data.user.role === 'ADMIN'"
            >门类信息</el-menu-item>
            <el-menu-item
              index="/manager/specialtys"
              v-if="data.user.role === 'ADMIN'"
            >专业信息</el-menu-item>
            <el-menu-item
              index="/manager/interpretations"
              v-if="data.user.role === 'ADMIN'"
            >专业解读</el-menu-item>
            <el-menu-item index="/manager/universitySpecialtys">学校专业</el-menu-item>
            <el-menu-item index="/manager/policys">招生政策</el-menu-item>
            <el-menu-item index="/manager/comment">学校评价</el-menu-item>
            <el-menu-item
              index="/manager/slideshow"
              v-if="data.user.role === 'ADMIN'"
            >轮播图信息</el-menu-item>
            <el-menu-item
              index="/manager/notice"
              v-if="data.user.role === 'ADMIN'"
            >系统公告</el-menu-item>
            <el-menu-item
              index="/manager/question"
              v-if="data.user.role === 'ADMIN'"
            >题库管理</el-menu-item>
            <el-menu-item
              index="/manager/knowledgeBase"
              v-if="data.user.role === 'ADMIN'"
            >知识库管理</el-menu-item>

            <!-- 新菜单 -->
          </el-sub-menu>
          <el-sub-menu
            index="2"
            v-if="data.user.role === 'ADMIN'"
          >
            <template #title>
              <el-icon>
                <UserFilled />
              </el-icon>
              <span>用户管理</span>
            </template>
            <el-menu-item index="/manager/admin">管理员信息</el-menu-item>
            <el-menu-item index="/manager/university">大学信息</el-menu-item>
            <el-menu-item index="/manager/user">学生信息</el-menu-item>
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
  user: JSON.parse(localStorage.getItem("xm-user") || "{}"),
});

const logout = () => {
  localStorage.removeItem("xm-user");
  router.push("/login");
};

const updateUser = () => {
  data.user = JSON.parse(localStorage.getItem("xm-user") || "{}");
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
