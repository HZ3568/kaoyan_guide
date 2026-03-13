<template>
  <div>
    <div class="card" style="margin-bottom: 5px;">
      <el-input v-model="data.specialtysName" placeholder="请输入专业名称查询" style="width: 240px"></el-input>
      <el-button type="info" plain style="margin-left: 10px" @click="load">查询</el-button>
      <el-button type="warning" plain style="margin-left: 10px" @click="reset">重置</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px">
      <el-button type="danger" plain @click="delBatch">批量删除</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px;">
      <el-table :data="data.tableData" stripe @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="universityName" label="学校名称"></el-table-column>
        <el-table-column prop="categorysName" label="门类名称"></el-table-column>
        <el-table-column prop="specialtysName" label="专业名称"></el-table-column>
        <el-table-column label="查看内容">
          <template v-slot="scope">
            <el-button type="primary" @click="preview(scope.row.content)">查看内容</el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template v-slot="scope">
            <el-button type="danger" circle :icon="Delete" @click="del(scope.row.id)"></el-button>
          </template>
        </el-table-column>
      </el-table>

    </div>
    <div class="card" v-if="data.total">
      <el-pagination @current-change="load" background layout="total, prev, pager, next" :page-size="data.pageSize" v-model:current-page="data.pageNum" :total="data.total"/>
    </div>

    <el-dialog title="学校专业" v-model="data.formVisible" width="50%" :close-on-click-modal="false" destroy-on-close>
      <el-form :model="data.form" :rules="data.rules" label-width="80px"  style="padding: 20px 30px" ref="formRef">
        <el-form-item label="所属门类" prop="categorysId">
          <el-select style="width: 100%" v-model="data.form.categorysId" placeholder="请选择专业门类" @change="loadSpecialtys(null)">
            <el-option v-for="item in data.categorysList" :key="item.id" :value="item.id" :label="item.name"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="所属专业" prop="specialtysId">
          <el-select style="width: 100%" v-model="data.form.specialtysId" placeholder="请选择专业">
            <el-option v-for="item in data.specialtysList" :key="item.id" :value="item.id" :label="item.name"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="专业介绍" prop="content">
          <div style="border: 1px solid #ccc; width: 100%">
            <Toolbar
                style="border-bottom: 1px solid #ccc"
                :editor="editorRef"
                :mode="mode"
            />
            <Editor
                style="height: 500px; overflow-y: hidden;"
                v-model="data.form.content"
                :mode="mode"
                :defaultConfig="editorConfig"
                @onCreated="handleCreated"
            />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="data.formVisible = false">取消</el-button>
          <el-button type="primary" @click="save">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog title="内容" v-model="data.fromVisibleContent" width="50%" :close-on-click-modal="false" destroy-on-close>
      <div style="padding: 15px">
        <div v-html="data.content"></div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="data.fromVisibleContent = false">关闭</el-button>
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
import '@wangeditor/editor/dist/css/style.css' // 引入 css
import {onBeforeUnmount, shallowRef} from "vue";
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'

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
  specialtysName: null,
  rules: {
    categorysId: [
      { required: true, message: '请选择门类', trigger: 'blur' },
    ],
    specialtysId: [
      { required: true, message: '请选择专业', trigger: 'blur' },
    ],
    content: [
      { required: true, message: '请输入专业介绍', trigger: 'blur' },
    ],
  },
  categorysList: [],
  specialtysList: [],
  content: '',
  fromVisibleContent: false,
})

/* wangEditor5 初始化开始 */
const editorRef = shallowRef()  // 编辑器实例，必须用 shallowRef
const mode = 'default' 
const editorConfig = { MENU_CONF: {} }
// 图片上传配置
editorConfig.MENU_CONF['uploadImage'] = {
  headers: {
    token: data.user.token,
  },
  server: baseUrl + '/files/wang/upload',  // 服务端图片上传接口
  fieldName: 'file'  // 服务端图片上传接口参数
}
// 组件销毁时，也及时销毁编辑器，否则可能会造成内存泄漏
onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})
// 记录 editor 实例，重要！
const handleCreated = (editor) => {
  editorRef.value = editor 
}
/* wangEditor5 初始化结束 */

const preview = (content) => {
  data.content = content
  data.fromVisibleContent = true
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
loadCategorys()
const loadSpecialtys = (categorysId) => {
  if (categorysId === null) {
    data.form.specialtysId = null
    categorysId = data.form.categorysId
  }
  request.get('/specialtys/selectAll', {
    params: {
      categorysId: categorysId
    }
  }).then(res => {
    if (res.code === '200') {
      data.specialtysList = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}
// 加载表格数据
const load = () => {
  request.get('/universitySpecialtys/selectPage', {
    params: {
      pageNum: data.pageNum,
      pageSize: data.pageSize,
      specialtysName: data.specialtysName
    }
  }).then(res => {
    data.tableData = res.data?.list || []
    data.total = res.data?.total
  })
}

// 打开新增弹窗
const handleAdd = () => {
  data.form = {}
  data.formVisible = true
}

// 打开编辑弹窗
const handleEdit = (row) => {
  data.form = JSON.parse(JSON.stringify(row))
  loadSpecialtys(data.form.categorysId)
  data.formVisible = true
}

// 新增
const add = () => {
  request.post('/universitySpecialtys/add', data.form).then(res => {
    if (res.code === '200') {
      data.formVisible = false
      ElMessage.success('操作成功')
      load()
    } else {
      ElMessage.error(res.msg)
    }
  })
}

// 更新
const update = () => {
  request.put('/universitySpecialtys/update', data.form).then(res => {
    if (res.code === '200') {
      data.formVisible = false
      ElMessage.success('操作成功')
      load()
    } else {
      ElMessage.error(res.msg)
    }
  })
}

// 删除
const del = (id) => {
  ElMessageBox.confirm('删除后数据无法恢复，您确定删除吗?', '删除确认', { type: 'warning' }).then(res => {
    request.delete('/universitySpecialtys/delete/' + id).then(res => {
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
    request.delete('/universitySpecialtys/delete/batch', {data: data.ids}).then(res => {
      if (res.code === '200') {
        ElMessage.success('操作成功')
        load()  // 刷新表格数据
      } else {
        ElMessage.error(res.msg)
      }
    })
  }).catch(err => console.log(err))
}

const save = () => {
  formRef.value.validate(valid => {
    if (valid) {
      data.form.id ? update() : add()
    }
  })
}

const reset = () => {
  data.specialtysName = null
  load()
}

load()

</script>
