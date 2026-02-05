<template>
  <div class="main-content">
    <div class="front-card">
      <div style="font-size: 24px; font-weight: bold; margin-bottom: 20px">我的志愿</div>
      <div style="margin-bottom: 20px">
        <el-table :data="data.tableData" stripe>
          <el-table-column prop="score" label="高考分数"></el-table-column>
          <el-table-column prop="ranking" label="省排名"></el-table-column>
          <el-table-column prop="areasName" label="考试地区"></el-table-column>
          <el-table-column prop="firstUniversityName" label="第一志愿学校" width="120"></el-table-column>
          <el-table-column prop="firstSpecialtysName" label="第一志愿专业" width="120"></el-table-column>
          <el-table-column prop="firstStatus" label="第一志愿状态" width="120">
            <template v-slot="scope">
              <el-tag type="warning" v-if="scope.row.firstStatus === '待录取'">待录取</el-tag>
              <el-tag type="success" v-if="scope.row.firstStatus === '已录取'">已录取</el-tag>
              <el-tag type="danger" v-if="scope.row.firstStatus === '未录取'">未录取</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="secondUniversityName" label="第二志愿学校" width="120"></el-table-column>
          <el-table-column prop="secondSpecialtysName" label="第二志愿专业" width="120"></el-table-column>
          <el-table-column prop="secondStatus" label="第二志愿状态" width="120">
            <template v-slot="scope">
              <el-tag type="warning" v-if="scope.row.secondStatus === '待录取'">待录取</el-tag>
              <el-tag type="success" v-if="scope.row.secondStatus === '已录取'">已录取</el-tag>
              <el-tag type="danger" v-if="scope.row.secondStatus === '未录取'">未录取</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="thirdUniversityName" label="第三志愿学校" width="120"></el-table-column>
          <el-table-column prop="thirdSpecialtysName" label="第三志愿专业" width="120"></el-table-column>
          <el-table-column prop="thirdStatus" label="第三志愿状态" width="120">
            <template v-slot="scope">
              <el-tag type="warning" v-if="scope.row.thirdStatus === '待录取'">待录取</el-tag>
              <el-tag type="success" v-if="scope.row.thirdStatus === '已录取'">已录取</el-tag>
              <el-tag type="danger" v-if="scope.row.thirdStatus === '未录取'">未录取</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="志愿状态">
            <template v-slot="scope">
              <el-tag type="warning" v-if="scope.row.status === '待录取'">待录取</el-tag>
              <el-tag type="success" v-if="scope.row.status === '已录取'">已录取</el-tag>
              <el-tag type="danger" v-if="scope.row.status === '未录取'">未录取</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="time" label="报考时间" show-overflow-tooltip></el-table-column>
        </el-table>

      </div>
      <div v-if="data.total">
        <el-pagination @current-change="load" layout="total, prev, pager, next" :page-size="data.pageSize" v-model:current-page="data.pageNum" :total="data.total"/>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue"
import request from "@/utils/request";
import {ElMessage, ElMessageBox} from "element-plus";
import {Delete, Edit} from "@element-plus/icons-vue";
const baseUrl = import.meta.env.VITE_BASE_URL
const formRef = ref()
const data = reactive({
  user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
  tableData: [],
  total: 0,
  pageNum: 1,  // 当前的页码
  pageSize: 5,  // 每页的个数
  formVisible: false,
  form: {},
  ids: [],
  userName: null,
})
// 加载表格数据
const load = () => {
  request.get('/apply/selectPage', {
    params: {
      pageNum: data.pageNum,
      pageSize: data.pageSize,
      userName: data.userName
    }
  }).then(res => {
    data.tableData = res.data?.list || []
    data.total = res.data?.total
  })
}

// 删除
const del = (id) => {
  ElMessageBox.confirm('删除后数据无法恢复，您确定删除吗?', '删除确认', { type: 'warning' }).then(res => {
    request.delete('/apply/delete/' + id).then(res => {
      if (res.code === '200') {
        ElMessage.success('删除成功')
        load()
      } else {
        ElMessage.error(res.msg)
      }
    })
  }).catch(err => {
    console.error(err)
  })
}

// 批量删除
const handleSelectionChange = (rows) => {
  data.ids = rows.map(v => v.id)
}

const delBatch = () => {
  if (!data.ids.length) {
    ElMessage.warning("请选择数据")
    return
  }
  ElMessageBox.confirm('删除后数据无法恢复，您确定删除吗?', '删除确认', { type: 'warning' }).then(res => {
    request.delete('/apply/delete/batch', {data: data.ids}).then(res => {
      if (res.code === '200') {
        ElMessage.success('操作成功')
        load()  // 刷新表格数据
      } else {
        ElMessage.error(res.msg)
      }
    })
  }).catch(err => console.log(err))
}


const reset = () => {
  data.userName = null
  load()
}

load()
</script>