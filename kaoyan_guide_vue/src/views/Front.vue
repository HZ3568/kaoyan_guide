<template>
  <div>
    <div class="front-header">
      <div class="front-header-left">
        <img src="@/assets/imgs/logo.png" alt="" />
        <div class="title" @click="router.push('/front/home')">
          高考志愿填报
        </div>
      </div>
      <div class="front-header-center">
        <el-menu
          :default-active="router.currentRoute.value.path"
          router
          mode="horizontal"
        >
          <el-menu-item index="/front/home">首页</el-menu-item>
          <el-menu-item index="/front/addApply">志愿填报</el-menu-item>
          <el-menu-item index="/front/universityList">院校库</el-menu-item>
          <el-menu-item index="/front/interpretationsList"
            >专业解读</el-menu-item
          >
          <el-menu-item index="/front/newsList">高考资讯</el-menu-item>
          <el-menu-item index="/front/policysList">招生政策</el-menu-item>
          <el-menu-item index="/front/simulateExam">考场模拟</el-menu-item>
          <el-menu-item index="/front/consultCollege"
            >AI院校信息咨询</el-menu-item
          >
          <el-menu-item index="/front/studyPlan">AI学习规划</el-menu-item>
          <el-menu-item index="/front/test">测试</el-menu-item>
        </el-menu>
      </div>
      <div class="front-header-right">
        <div v-if="!data.user.id">
          <el-button @click="router.push('/login')">登录</el-button>
          <el-button @click="router.push('/register')">注册</el-button>
        </div>
        <div v-else>
          <el-dropdown style="cursor: pointer; height: 60px">
            <div style="display: flex; align-items: center">
              <img
                style="width: 40px; height: 40px; border-radius: 50%"
                :src="data.user.avatar"
                alt=""
              />
              <span style="margin-left: 5px">{{ data.user.name }}</span
              ><el-icon><arrow-down /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click.native="router.push('/front/myApply')"
                  >我的志愿</el-dropdown-item
                >
                <el-dropdown-item
                  @click.native="router.push('/front/myComment')"
                  >我的评价</el-dropdown-item
                >
                <el-dropdown-item
                  @click.native="router.push('/front/myCollect')"
                  >我的收藏</el-dropdown-item
                >
                <el-dropdown-item
                  @click.native="router.push('/front/noticeList')"
                  >公告信息</el-dropdown-item
                >
                <el-dropdown-item @click.native="router.push('/front/person')"
                  >个人中心</el-dropdown-item
                >
                <el-dropdown-item
                  @click.native="router.push('/front/certification')"
                  >学籍认证</el-dropdown-item
                >
                <el-dropdown-item @click.native="router.push('/front/password')"
                  >修改密码</el-dropdown-item
                >
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>
    <div class="main-body">
      <RouterView @updateUser="updateUser" />
    </div>
    <Footer />
  </div>
</template>

<script setup>
import router from "@/router/index.js";
import { reactive } from "vue";
import request from "@/utils/request.js";

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
</script>

<style scoped>
@import "@/assets/css/front.css";
</style>