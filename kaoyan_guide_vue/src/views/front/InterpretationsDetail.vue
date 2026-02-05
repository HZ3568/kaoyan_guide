<template>
  <div style="width: 60%; margin: 20px auto; min-height: 100vh">
    <div class="front-card" style="margin-bottom: 20px">
      <div style="font-weight: bold; font-size: 24px; text-align: center; ">
        {{data.interpretationsInfo.name}}
      </div>
      <div style="margin-top: 10px; color: #666; text-align: center; margin-bottom: 20px">
        <span style="margin-left: 20px">专业门类: {{data.interpretationsInfo.categorysName}}</span>
        <span style="margin-left: 20px">发布时间: {{data.interpretationsInfo.time}}</span>
        <span style="margin-left: 20px">浏览量: {{data.interpretationsInfo.viewCount}}</span>
      </div>
      <div style="padding: 20px">
        <div v-html="data.interpretationsInfo.content"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {useRoute} from "vue-router"
import request from "@/utils/request";
import {reactive, onMounted} from "vue";
import {ElMessage, ElMessageBox} from "element-plus";
import router from "@/router/index.js";
import '@/assets/css/view.css'
const route = useRoute();
const interpretationsId = route.query.id;

const data = reactive({
  user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
  interpretationsInfo: {}
})

const loadInterpretationsById = () => {
  request.get('/interpretations/selectById/' + interpretationsId).then(res => {
    if (res.code === '200') {
      data.interpretationsInfo = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}

const loadUpdateViewCount = () => {
  request.get('/interpretations/loadUpdateViewCount/' + interpretationsId).then(res => {
    if (res.code === '200') {
      loadInterpretationsById()
    } else {
      ElMessage.error(res.msg)
    }
  })
}

onMounted(()=>{
  loadUpdateViewCount()
})

</script>