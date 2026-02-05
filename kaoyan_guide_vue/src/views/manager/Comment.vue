<template>
  <div>
    <div class="card" style="margin-bottom: 5px;">
      <el-input v-model="data.details" placeholder="请输入评价内容查询" style="width: 240px"></el-input>
      <el-button type="info" plain style="margin-left: 10px" @click="load">查询</el-button>
      <el-button type="warning" plain style="margin-left: 10px" @click="reset">重置</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px" v-if="data.user.role === 'ADMIN'">
      <el-button type="danger" plain @click="delBatch">批量删除</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px;">
      <el-table :data="data.tableData" tooltip-effect="dark myTooltip" stripe @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" v-if="data.user.role === 'ADMIN'"></el-table-column>
        <el-table-column prop="universityName" label="大学名称"></el-table-column>
        <el-table-column prop="userName" label="学生名称"></el-table-column>
        <el-table-column prop="details" label="评价内容" show-overflow-tooltip></el-table-column>
        <el-table-column prop="mark" label="评分">
          <template v-slot="scope">
            <el-rate v-model="scope.row.mark" disabled/>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="创建时间"></el-table-column>
        <el-table-column label="操作" width="100" fixed="right" v-if="data.user.role === 'ADMIN'">
          <template v-slot="scope">
            <el-button type="danger" circle :icon="Delete" @click="del(scope.row.id)"></el-button>
          </template>
        </el-table-column>
      </el-table>

    </div>
    <div class="card" v-if="data.total">
      <el-pagination @current-change="load" background layout="total, prev, pager, next" :page-size="data.pageSize" v-model:current-page="data.pageNum" :total="data.total"/>
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
  details: null,
})

// 加载表格数据
const load = () => {
  request.get('/comment/selectPage', {
    params: {
      pageNum: data.pageNum,
      pageSize: data.pageSize,
      details: data.details
    }
  }).then(res => {
    data.tableData = res.data?.list || []
    data.total = res.data?.total
  })
}


// 删除
const del = (id) => {
  ElMessageBox.confirm('删除后数据无法恢复，您确定删除吗?', '删除确认', { type: 'warning' }).then(res => {
    request.delete('/comment/delete/' + id).then(res => {
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
    request.delete('/comment/delete/batch', {data: data.ids}).then(res => {
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
  data.details = null
  load()
}

load()

</script>

<style>
.myTooltip {
  max-width: 40% !important;
}
</style>