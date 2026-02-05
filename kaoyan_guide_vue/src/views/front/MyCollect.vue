<template>
  <div class="main-content">
    <div style="font-size: 24px; font-weight: bold; margin-bottom: 20px">我的收藏（{{data.tableData?.length}}）</div>
    <el-row :gutter="20">
      <el-col :span="5" v-for="item in data.tableData" :key="item.id" >
        <div class="card" style="margin-bottom: 20px; cursor: pointer" >
          <img alt="" :src="item.universityAvatar" style="width: 100%; height: 200px; border-radius: 5px 5px 0 0" @click="$router.push('/front/universityDetail?id=' + item.universityId)">
          <div style="padding: 10px">
            <div class="line1" style="font-size: 20px; font-weight: bold; margin-bottom: 10px">{{item.universityName}}</div>
            <el-button type="danger" @click="del(item.id)">取消收藏</el-button>
          </div>
        </div>

      </el-col>
    </el-row>
    <div v-if="data.total">
      <el-pagination @current-change="load" layout="total, prev, pager, next" :page-size="data.pageSize" v-model:current-page="data.pageNum" :total="data.total"/>
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue"
import request from "@/utils/request";
import {ElMessage, ElMessageBox} from "element-plus";

const baseUrl = import.meta.env.VITE_BASE_URL
const data = reactive({
  user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
  tableData: [],
  total: 0,
  pageNum: 1,  // 当前的页码
  pageSize: 8,  // 每页的个数
})

// 加载表格数据
const load = () => {
  request.get('/collect/selectPage', {
    params: {
      pageNum: data.pageNum,
      pageSize: data.pageSize,
    }
  }).then(res => {
    data.tableData = res.data?.list || []
    data.total = res.data?.total
  })
}

load()

const del = (id) => {
  ElMessageBox.confirm('您确定取消收藏该学校吗?', '取消确认', { type: 'warning' }).then(res => {
    request.delete('/collect/delete/' + id).then(res => {
      if (res.code === '200') {
        ElMessage.success('取消成功')
        load()
      } else {
        ElMessage.error(res.msg)
      }
    })
  }).catch(err => {
    console.error(err)
  })
}
</script>

<style scoped>

.el-col-5 {
  width: 20%;
  max-width: 20%;
}
</style>
