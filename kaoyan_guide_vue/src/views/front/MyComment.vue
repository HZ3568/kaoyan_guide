<template>
  <div class="main-content">
    <div class="front-card">
      <div style="font-size: 24px; font-weight: bold; margin-bottom: 20px">我的评论</div>
      <div>
        <el-input v-model="data.details" placeholder="请输入评价内容查询" style="width: 240px"></el-input>
        <el-button type="info" plain style="margin-left: 10px" @click="load">查询</el-button>
        <el-button type="warning" plain style="margin-left: 10px" @click="reset">重置</el-button>
      </div>

      <div style="margin: 20px 0">
        <el-table :data="data.tableData" stripe>
          <el-table-column prop="universityName" label="大学名称"></el-table-column>
          <el-table-column prop="details" label="评价内容"></el-table-column>
          <el-table-column prop="mark" label="评分">
            <template v-slot="scope">
              <el-rate v-model="scope.row.mark" disabled/>
            </template>
          </el-table-column>
          <el-table-column prop="time" label="创建时间"></el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template v-slot="scope">
              <el-button type="primary" circle :icon="Edit" @click="handleEdit(scope.row)"></el-button>
              <el-button type="danger" circle :icon="Delete" @click="del(scope.row.id)"></el-button>
            </template>
          </el-table-column>
        </el-table>

      </div>
      <div v-if="data.total">
        <el-pagination @current-change="load" layout="total, prev, pager, next" :page-size="data.pageSize" v-model:current-page="data.pageNum" :total="data.total"/>
      </div>
    </div>
    <el-dialog title="学校评价" v-model="data.formVisible" width="40%" destroy-on-close>
      <el-form ref="formRef" :rules="data.rules" :model="data.form" label-width="80px" style="padding: 20px">
        <el-form-item prop="details" label="评价内容">
          <el-input v-model="data.form.details" placeholder="请输入评价内容" type="textarea" rows="4"></el-input>
        </el-form-item>
        <el-form-item prop="mark" label="评分">
          <el-rate v-model="data.form.mark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="data.formVisible = false">取 消</el-button>
          <el-button type="primary" @click="update">确 定</el-button>
        </span>
      </template>
    </el-dialog>

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
  rules: {
    details: [
      { required: true, message: '请输入评价内容', trigger: 'blur' },
    ],
    mark: [
      { required: true, message: '请选择评分', trigger: 'blur' },
    ],
  },
})

// 加载表格数据
const load = () => {
  request.get('/comment/selectPage', {
    params: {
      pageNum: data.pageNum,
      pageSize: data.pageSize,
      details: data.details,
      userId: data.user.id
    }
  }).then(res => {
    data.tableData = res.data?.list || []
    data.total = res.data?.total
  })
}
const handleEdit = (row) => {
  data.form = JSON.parse(JSON.stringify(row))
  data.formVisible = true
}
const update = () => {
  formRef.value.validate(valid => {
    if (valid) {
      request.put('/comment/update', data.form).then(res => {
        if (res.code === '200') {
          ElMessage.success('修改成功')
          data.formVisible = false
          load()
        } else {
          ElMessage.error(res.msg)
        }
      })
    }
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