<template>
  <div>
    <div class="card" style="margin-bottom: 5px;">
      <el-input v-model="data.universityName" placeholder="请输入大学名称查询" style="width: 240px"></el-input>
      <el-select v-model="data.status" placeholder="请选择认证状态查询" style="width: 240px; margin-left: 10px">
        <el-option label="待审核" value="待审核"></el-option>
        <el-option label="审核通过" value="审核通过"></el-option>
        <el-option label="审核拒绝" value="审核拒绝"></el-option>
      </el-select>
      <el-button type="info" plain style="margin-left: 10px" @click="load">查询</el-button>
      <el-button type="warning" plain style="margin-left: 10px" @click="reset">重置</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px">
      <el-button type="danger" plain @click="delBatch">批量删除</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px;">
      <el-table :data="data.tableData" stripe @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="universityName" label="大学名称"></el-table-column>
        <el-table-column prop="universityCode" label="学校代码"></el-table-column>
        <el-table-column label="办学许可证">
          <template #default="scope">
            <el-image style="width: 40px; height: 40px; border-radius: 5px" v-if="scope.row.licenseImg" :src="scope.row.licenseImg" :preview-src-list="[scope.row.licenseImg]" preview-teleported></el-image>
          </template>
        </el-table-column>
        <el-table-column label="招生资格认证">
          <template #default="scope">
            <el-image style="width: 40px; height: 40px; border-radius: 5px" v-if="scope.row.qualificationsImg" :src="scope.row.qualificationsImg" :preview-src-list="[scope.row.qualificationsImg]" preview-teleported></el-image>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="认证状态">
          <template v-slot="scope">
            <el-tag type="warning" v-if="scope.row.status === '待审核'">待审核</el-tag>
            <el-tag type="success" v-if="scope.row.status === '审核通过'">审核通过</el-tag>
            <el-tag type="danger" v-if="scope.row.status === '审核拒绝'">审核拒绝</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="refuseReason" label="拒绝理由"></el-table-column>
        <el-table-column prop="time" label="创建时间"></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template v-slot="scope">
            <el-button type="primary" @click="handleEdit(scope.row)" :disabled="scope.row.status !== '待审核'">审核</el-button>
            <el-button type="danger" circle :icon="Delete" @click="del(scope.row.id)"></el-button>
          </template>
        </el-table-column>
      </el-table>

    </div>
    <div class="card" v-if="data.total">
      <el-pagination @current-change="load" background layout="total, prev, pager, next" :page-size="data.pageSize" v-model:current-page="data.pageNum" :total="data.total"/>
    </div>

    <el-dialog title="大学认证信息" v-model="data.formVisible" width="40%" :close-on-click-modal="false" destroy-on-close>
      <el-form :model="data.form" :rules="data.rules" label-width="80px"  style="padding: 20px 30px" ref="formRef">
        <el-form-item label="认证状态" prop="status">
          <el-radio-group v-model="data.form.status">
            <el-radio-button label="审核通过" value="审核通过" />
            <el-radio-button label="审核拒绝" value="审核拒绝" />
          </el-radio-group>
        </el-form-item>
        <el-form-item label="拒绝理由" prop="refuseReason" v-if="data.form.status === '审核拒绝'">
          <el-input v-model="data.form.refuseReason" placeholder="拒绝理由" type="textarea" rows="4"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="data.formVisible = false">取消</el-button>
          <el-button type="primary" @click="update">保存</el-button>
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
  universityName: null,
  status: null,
  rules: {
    status: [
      { required: true, message: '请选择认证状态', trigger: 'blur' },
    ],
    refuseReason: [
      { required: true, message: '请输入拒绝理由', trigger: 'blur' },
    ],
  },
  universityList: [],
})


// 加载表格数据
const load = () => {
  request.get('/universityCertification/selectPage', {
    params: {
      pageNum: data.pageNum,
      pageSize: data.pageSize,
      universityName: data.universityName,
      status: data.status
    }
  }).then(res => {
    data.tableData = res.data?.list || []
    data.total = res.data?.total
  })
}
// 打开编辑弹窗
const handleEdit = (row) => {
  data.form = JSON.parse(JSON.stringify(row))
  data.form.status = '审核通过'
  data.formVisible = true
}

// 更新
const update = () => {
  formRef.value.validate(valid => {
    if (valid) {
      request.put('/universityCertification/update', data.form).then(res => {
        if (res.code === '200') {
          data.formVisible = false
          ElMessage.success('操作成功')
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
    request.delete('/universityCertification/delete/' + id).then(res => {
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
    request.delete('/universityCertification/delete/batch', {data: data.ids}).then(res => {
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
  data.universityName = null
  data.status = null
  load()
}

load()

</script>