<template>
  <div style="width: 60%; margin: 20px auto; min-height: 100vh">
    <div style="border: 1px solid #eeeeee; padding: 15px 30px; border-radius: 5px; margin-bottom: 20px">
      <div style="border-bottom: 1px solid #eeeeee; padding: 10px 0">
        <div style="display: flex; align-items: center; flex-wrap: wrap">
          <div @click="changeCategorysFlag(null)" style="padding-bottom: 5px; margin-right: 20px; cursor: pointer; margin-bottom: 10px" :class="{'category-active' : data.categorysFlag === null }">全部</div>
          <div @click="changeCategorysFlag(item.id)" style="padding-bottom: 5px; margin-right: 20px; cursor: pointer; margin-bottom: 10px" :class="{'category-active' : data.categorysFlag === item.id }" v-for="item in data.categorysList" :key="item.id">{{ item.name }}</div>
        </div>
      </div>
    </div>
    <div>
      <el-row :gutter="15">
        <el-col :span="8" v-for="item in data.tableData" style="margin-bottom: 20px">
          <div class="card" style="padding: 0; margin-bottom: 20px; cursor: pointer" @click="$router.push('/front/interpretationsDetail?id=' + item.id)">
            <img alt="" :src="item.img" style="width: 100%; height: 240px; border-radius: 5px 5px 0 0">
            <div style="padding: 10px">
              <div class="line1" style="font-size: 20px; font-weight: bold; margin-bottom: 10px">{{item.name}}</div>
              <div class="line2" style="height: 40px; line-height: 20px; margin-bottom: 10px">{{item.intro}}</div>
              <div>浏览量：{{item.viewCount}}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
    <div v-if="data.total">
      <el-pagination @current-change="load" layout="total, prev, pager, next" :page-size="data.pageSize" v-model:current-page="data.pageNum" :total="data.total" />
    </div>
  </div>
</template>

<script setup>
import {reactive, ref} from "vue";
import request from "@/utils/request.js";
import {ElMessage} from "element-plus";
import router from "@/router/index.js";

const data = reactive({
  categorysFlag: null,
  categorysList: [],
  pageNum: 1,
  pageSize: 6,
  total: 0,
  tableData: []
})
const load = () => {
  request.get('/interpretations/selectPage', {
    params: {
      pageNum: data.pageNum,
      pageSize: data.pageSize,
      categorysId: data.categorysFlag,
    }
  }).then(res => {
    if (res.code === '200') {
      data.tableData = res.data.list
      data.total = res.data.total
    } else {
      ElMessage.error(res.msg)
    }
  })
}
const loadCategorys = () => {
  request.get('/categorys/selectAll').then(res => {
    if (res.code === '200') {
      data.categorysList = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}

const changeCategorysFlag = (id) => {
  data.categorysFlag = id
  load()
}

loadCategorys()
load()
</script>

<style scoped>
.category-active {
  color: #006cff;
  border-bottom: 2px solid #006cff;
}

.el-col-5 {
  width: 20%;
  max-width: 20%;
}
</style>