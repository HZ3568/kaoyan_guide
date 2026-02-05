<template>
  <div style="width: 60%; margin: 20px auto; min-height: 100vh">
    <div>
      <div style="margin-bottom: 20px;">
        <div style="display: flex">
          <el-input v-model="data.name" placeholder="请输入资讯标题查询" style="width: 400px; height: 40px" clearable @clear="load" @keyup.enter="load"></el-input>
          <el-button type="info" plain style="margin-left: 10px; height: 40px; width: 100px" @click="load">查询</el-button>
        </div>
      </div>
      <div>
        <div @click="$router.push('/front/newsDetail?id=' + item.id)" style="margin-bottom: 10px; padding: 0" class="card" v-for="(item,index) in data.tableData" :key="item.id" v-if="data.tableData?.length !== 0">
          <div v-if="index % 2 === 0" style="display: flex; grid-gap: 20px; cursor: pointer; margin-bottom: 20px" class="card">
            <img style="width: 150px; height: 100px; border-radius: 5px; cursor: pointer" :src="item.img" alt="" />
            <div style="flex: 1; width: 0">
              <div style="font-size: 16px; font-weight: bold" class="line1">{{ item.name }}</div>
              <div style="margin-top: 10px; line-height: 20px; height: 40px; color: #666" class="line2">{{ item.intro }}</div>
              <div style="margin-top: 10px; display: flex; align-items: center; color: #666; font-size: 13px">
                <div style="display: flex; align-items: center; margin-right: 20px">
                  <el-icon size="16"><View /></el-icon>
                  <span style="margin-left: 5px">{{ item.viewCount }}</span>
                </div>
                <div style="display: flex; align-items: center">
                  <el-icon size="16"><Clock /></el-icon>
                  <span style="margin-left: 5px">{{ item.time }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else style="display: flex; grid-gap: 20px; cursor: pointer; margin-bottom: 20px" class="card">
            <div style="flex: 1; width: 0">
              <div style="font-size: 16px; font-weight: bold" class="line1">{{ item.name }}</div>
              <div style="margin-top: 10px; line-height: 20px; height: 40px; color: #666" class="line2">{{ item.intro }}</div>
              <div style="margin-top: 10px; display: flex; align-items: center; color: #666; font-size: 13px">
                <div style="display: flex; align-items: center; margin-right: 20px">
                  <el-icon size="16"><View /></el-icon>
                  <span style="margin-left: 5px">{{ item.viewCount }}</span>
                </div>
                <div style="display: flex; align-items: center">
                  <el-icon size="16"><Clock /></el-icon>
                  <span style="margin-left: 5px">{{ item.time }}</span>
                </div>
              </div>
            </div>
            <img style="width: 150px; height: 100px; border-radius: 5px; cursor: pointer" :src="item.img" alt="" />
          </div>
        </div>
        <div v-else class="card" style="padding: 20px; font-size: 20px; color: #666666">......暂无资讯</div>
        <div style="margin-top: 20px" v-if="data.total">
          <el-pagination @current-change="load" layout="total, prev, pager, next" :page-size="data.pageSize" v-model:current-page="data.pageNum" :total="data.total"/>
        </div>
      </div>
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
  pageSize: 10,  // 每页的个数
  name: null,
})

// 加载表格数据
const load = () => {
  request.get('/news/selectPage', {
    params: {
      pageNum: data.pageNum,
      pageSize: data.pageSize,
      name: data.name
    }
  }).then(res => {
    data.tableData = res.data?.list || []
    data.total = res.data?.total
  })
}

load()
</script>

<style scoped>
</style>