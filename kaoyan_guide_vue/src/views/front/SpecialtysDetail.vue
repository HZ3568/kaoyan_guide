<template>
  <div style="width: 60%; margin: 20px auto; min-height: 100vh">
    <div class="front-card" style="margin-bottom: 20px">
      <div style="font-weight: bold; font-size: 24px; text-align: center; ">
        {{data.specialtysInfo.universityName}}<span style="font-size: 16px">----{{data.specialtysInfo.specialtysName}}</span>
      </div>
      <div style="padding: 20px">
        <div v-html="data.specialtysInfo.content"></div>
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
const specialtysId = route.query.id;

const data = reactive({
  user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
  specialtysInfo: {}
})

const loadSpecialtysById = () => {
  request.get('/universitySpecialtys/selectById/' + specialtysId).then(res => {
    if (res.code === '200') {
      data.specialtysInfo = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}
loadSpecialtysById()
</script>