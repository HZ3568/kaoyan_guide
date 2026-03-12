<template>
  <div style="width: 50%" class="card">
    <el-form ref="user" :model="data.user" label-width="70px" style="padding: 20px">
      <el-form-item prop="avatar" label="头像">
        <el-upload
            :action="baseUrl + '/files/upload'"
            :on-success="handleFileUpload"
            :show-file-list="false"
            class="avatar-uploader"
        >
          <img v-if="data.user.avatar" :src="data.user.avatar" class="avatar" @error="handleAvatarError" />
          <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
        </el-upload>
      </el-form-item>
      <el-form-item prop="username" label="用户名">
        <el-input disabled v-model="data.user.username" placeholder="请输入用户名"></el-input>
      </el-form-item>
      <el-form-item prop="name" label="名称">
        <el-input v-model="data.user.name" placeholder="请输入名称"></el-input>
      </el-form-item>
      <el-form-item prop="areasId" label="地区">
        <el-select v-model="data.user.areasId" style="width: 100%;" placeholder="请选择地区">
          <el-option :label="item.name" :value="item.id" v-for="item in data.areasList" :key="item.id"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item prop="address" label="详细地址">
        <el-input v-model="data.user.address" placeholder="请输入详细地址"></el-input>
      </el-form-item>
      <el-form-item prop="department" label="主管部门">
        <el-select v-model="data.user.department" style="width: 100%;" placeholder="请选择主管部门">
          <el-option label="教育部" value="教育部"></el-option>
          <el-option label="其他部委" value="其他部委"></el-option>
          <el-option label="地方" value="地方"></el-option>
          <el-option label="军校" value="军校"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item prop="level" label="办学层次">
        <el-select v-model="data.user.level" style="width: 100%;" placeholder="请选择办学层次">
          <el-option label="本科" value="本科"></el-option>
          <el-option label="高职(专科)" value="高职(专科)"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item prop="character" label="院校特性">
        <el-select v-model="data.user.characters" style="width: 100%;" placeholder="请选择主管部门">
          <el-option label="“双一流”建设高校" value="“双一流”建设高校"></el-option>
          <el-option label="民办高校" value="民办高校"></el-option>
          <el-option label="独立学院" value="独立学院"></el-option>
          <el-option label="中外合作办学" value="中外合作办学"></el-option>
          <el-option label="内地与港澳台地区合作办学" value="内地与港澳台地区合作办学"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item prop="officialWebsite" label="官方网址">
        <el-input v-model="data.user.officialWebsite" placeholder="请输入官方网址"></el-input>
      </el-form-item>
      <el-form-item prop="phone" label="电话">
        <el-input v-model="data.user.phone" placeholder="请输入电话"></el-input>
      </el-form-item>
      <el-form-item prop="email" label="邮箱">
        <el-input v-model="data.user.email" placeholder="请输入邮箱"></el-input>
      </el-form-item>
      <el-form-item prop="mark" label="满意度">
        <el-rate v-model="data.user.mark" disabled show-score text-color="#ff9900" score-template="满意度{value}"/>
      </el-form-item>
      <el-form-item prop="mark" label="院校简介">
        <div style="border: 1px solid #ccc; width: 100%">
          <Toolbar
              style="border-bottom: 1px solid #ccc"
              :editor="editorRef"
              :mode="mode"
          />
          <Editor
              style="height: 500px; overflow-y: hidden;"
              v-model="data.user.content"
              :mode="mode"
              :defaultConfig="editorConfig"
              @onCreated="handleCreated"
          />
        </div>
      </el-form-item>
      <div style="text-align: center">
        <el-button type="primary" @click="update">保 存</el-button>
      </div>
    </el-form>
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
import defaultAvatar from "@/assets/imgs/avatar.png";

const baseUrl = import.meta.env.VITE_BASE_URL

const data = reactive({
  user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
  areasList: []
})
const loadAreas = () => {
  request.get( '/areas/selectAll').then(res => {
    if (res.code === '200') {
      data.areasList = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}
loadAreas()
const handleFileUpload = (res) => {
  data.user.avatar = res.data
}

const handleAvatarError = (event) => {
  event.target.src = defaultAvatar
}

const emit = defineEmits(['updateUser'])
const update = () => {
  if (data.user.role === 'UNIVERSITY') {
    request.put('/university/update', data.user).then(res => {
      if (res.code === '200') {
        ElMessage.success('保存成功')
        localStorage.setItem('xm-user', JSON.stringify(data.user))
        emit('updateUser')
      } else {
        ElMessage.error(res.msg)
      }
    })
  }
}

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
</script>

<style>
.avatar-uploader {
  height: 120px;
}
.avatar-uploader .avatar {
  width: 120px;
  height: 120px;
  display: block;
}
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  text-align: center;
}
</style>
