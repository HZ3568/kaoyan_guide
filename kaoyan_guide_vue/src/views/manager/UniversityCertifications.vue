<template>
  <div style="width: 50%" class="card">
    <el-form ref="formRef" :rules="data.rules" :model="data.form" label-width="110px" style="padding: 20px">
      <el-form-item prop="universityCode" label="学校代码">
        <el-input v-model="data.form.universityCode" placeholder="请输入学校代码"></el-input>
      </el-form-item>
      <el-form-item prop="licenseImg" label="办学许可证">
        <el-upload
            :action="baseUrl + '/files/upload'"
            :on-success="handleLicenseImgSuccess"
            :show-file-list="false"
            class="avatar-uploader"
        >
          <img v-if="data.form.licenseImg" :src="data.form.licenseImg" class="avatar" />
          <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
        </el-upload>
      </el-form-item>

      <el-form-item prop="qualificationsImg" label="招生资格认证">
        <el-upload
            :action="baseUrl + '/files/upload'"
            :on-success="handleQualificationsImgSuccess"
            :show-file-list="false"
            class="avatar-uploader"
        >
          <img v-if="data.form.qualificationsImg" :src="data.form.qualificationsImg" class="avatar" />
          <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
        </el-upload>
      </el-form-item>
      <el-form-item prop="status" label="认证状态">
        <el-tag type="warning" style="background-color: orange; color: white" v-if="data.form.id === undefined">待提交</el-tag>
        <el-tag type="warning" v-if="data.form.status === '待审核'">待审核</el-tag>
        <el-tag type="success" v-if="data.form.status === '审核通过'">审核通过</el-tag>
        <el-tag type="danger" v-if="data.form.status === '审核拒绝'">审核拒绝</el-tag>
      </el-form-item>
      <el-form-item prop="refuseReason" label="拒绝理由" v-if="data.form.status === '审核拒绝'">
        <div style="color: red;">{{data.form.refuseReason}}</div>
      </el-form-item>
      <div style="text-align: center">
        <el-button type="primary" @click="save" :disabled="data.form.status === '审核通过'">提 交</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import {reactive, ref, onMounted} from "vue";
import request from "@/utils/request.js";
import {ElMessage} from "element-plus";

const baseUrl = import.meta.env.VITE_BASE_URL
const formRef = ref()
const data = reactive({
  user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
  form: {},
  rules: {
    universityCode: [
      { required: true, message: '请输入学校代码', trigger: 'blur' },
    ],
    licenseImg: [
      { required: true, message: '请上传办学许可证', trigger: 'blur' },
    ],
    qualificationsImg: [
      { required: true, message: '请上传招生资格认证', trigger: 'blur' },
    ],
  },
})
onMounted(()=>{
  loadCertification()
})
const handleLicenseImgSuccess = (res) => {
  data.form.licenseImg = res.data
}

const handleQualificationsImgSuccess = (res) => {
  data.form.qualificationsImg = res.data
}


// 新增
const add = () => {
  data.form.universityId = data.user.id
  request.post('/universityCertification/add', data.form).then(res => {
    if (res.code === '200') {
      ElMessage.success('提交成功')
      loadCertification()
    } else {
      ElMessage.error(res.msg)
    }
  })
}

// 更新
const update = () => {
  data.form.status = '待审核'
  data.form.refuseReason = ''
  request.put('/universityCertification/update', data.form).then(res => {
    if (res.code === '200') {
      ElMessage.success('提交成功')
      loadCertification()
    } else {
      ElMessage.error(res.msg)
    }
  })
}

const save = () => {
  formRef.value.validate(valid => {
    if (valid) {
      data.form.id ? update() : add()
    }
  })
}

const loadCertification = () => {
  request.get('/universityCertification/selectByUniversityId/' + data.user.id).then(res => {
    if (res.code === '200') {
      data.form = res.data || {}
    } else {
      ElMessage.error(res.msg)
    }
  })
}
loadCertification()
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