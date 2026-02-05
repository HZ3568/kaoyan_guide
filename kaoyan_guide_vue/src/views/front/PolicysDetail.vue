<template>
  <div style="width: 60%; margin: 20px auto; min-height: 100vh">
    <div class="front-card" style="margin-bottom: 20px">
      <div style="font-weight: bold; font-size: 24px; text-align: center; ">
        {{data.policysInfo.name}}
      </div>
      <div style="margin-top: 10px; color: #666; text-align: center; margin-bottom: 20px">
        <span style="margin-left: 20px">先关学校: {{data.policysInfo.universityName}}</span>
        <span style="margin-left: 20px">发布时间: {{data.policysInfo.time}}</span>
        <span style="margin-left: 20px">浏览量: {{data.policysInfo.viewCount}}</span>
      </div>
      <div style="padding: 20px">
        <div v-html="data.policysInfo.content"></div>
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
const policysId = route.query.id;

const data = reactive({
  user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
  policysInfo: {}
})

const loadPolicysById = () => {
  request.get('/policys/selectById/' + policysId).then(res => {
    if (res.code === '200') {
      data.policysInfo = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}

const loadUpdateViewCount = () => {
  request.get('/policys/loadUpdateViewCount/' + policysId).then(res => {
    if (res.code === '200') {
      loadPolicysById()
    } else {
      ElMessage.error(res.msg)
    }
  })
}

onMounted(()=>{
  loadUpdateViewCount()
})

</script>