<template>
  <div style="width: 50%; margin: 20px auto; min-height: 100vh">
    <div class="front-card">
      <div style="font-weight: bold; font-size: 24px; margin-bottom: 20px">系统公告</div>
      <el-timeline>
        <el-timeline-item
            v-for="(item, index) in data.noticeData"
            :key="index"
            :timestamp="item.time"
            placement="top"
        >
          <h4>{{ item.title }}</h4>
          <p>{{ item.content }}</p>
        </el-timeline-item>
      </el-timeline>
    </div>
  </div>
</template>

<script setup>

import {reactive} from "vue";
import request from "@/utils/request.js";
import {ElMessage} from "element-plus";

const data = reactive({
  user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
  noticeData: []
})

const loadNotice = () => {
  request.get('/notice/selectAll').then(res => {
    if (res.code === '200') {
      data.noticeData = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}
loadNotice()
</script>