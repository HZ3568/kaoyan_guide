<template>
  <div style="width: 50%; margin: 20px auto; min-height: 100vh">
    <div class="front-card">
      <div style="font-size: 24px; font-weight: bold; margin-bottom: 20px">学籍认证</div>
      <el-form ref="formRef" :rules="data.rules" :model="data.form" label-width="110px" style="padding: 20px">
        <el-form-item prop="candidateNumber" label="考生号">
          <el-input v-model="data.form.candidateNumber" placeholder="请输入考生号"></el-input>
        </el-form-item>
        <el-form-item prop="examinationNumber" label="准考证号">
          <el-input v-model="data.form.examinationNumber" placeholder="请输入准考证号"></el-input>
        </el-form-item>
        <el-form-item prop="score" label="高考分数">
          <el-input-number style="width: 300px" :min="0" :max="750" v-model="data.form.score" placeholder="请输入高考分数"></el-input-number>
        </el-form-item>
        <el-form-item prop="ranking" label="省排名">
          <el-input-number style="width: 300px" :min="1" :max="100000000" v-model="data.form.ranking" placeholder="请输入省排名"></el-input-number>
        </el-form-item>
        <el-form-item prop="areasId" label="考试省份">
          <el-select v-model="data.form.areasId" style="width: 100%" placeholder="请选择考试省份">
            <el-option :label="item.name" :value="item.id" v-for="item in data.areasList"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="identityNumber" label="身份证号">
          <el-input v-model="data.form.identityNumber" placeholder="请输入身份证号"></el-input>
        </el-form-item>
        <el-form-item prop="identityImg" label="身份证照片">
          <el-upload
              :action="baseUrl + '/files/upload'"
              :on-success="handleIdentityImgSuccess"
              :show-file-list="false"
              class="avatar-uploader"
          >
            <img v-if="data.form.identityImg" :src="data.form.identityImg" class="avatar" />
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
  areasList: [],
  rules: {
    candidateNumber: [
      { required: true, message: '请输入考生号', trigger: 'blur' },
    ],
    examinationNumber: [
      { required: true, message: '请输入准考证号', trigger: 'blur' },
    ],
    score: [
      { required: true, message: '请输入高考分数', trigger: 'blur' },
    ],
    ranking: [
      { required: true, message: '请输入省排名', trigger: 'blur' },
    ],
    areasId: [
      { required: true, message: '请选择考试省份', trigger: 'blur' },
    ],
    identityNumber: [
      { required: true, message: '请输入身份证号', trigger: 'blur' },
    ],
    identityImg: [
      { required: true, message: '请上传身份证照片', trigger: 'blur' },
    ],
  },
})
onMounted(()=>{
  loadCertification()
})
const handleIdentityImgSuccess = (res) => {
  data.form.identityImg = res.data
}


// 新增
const add = () => {
  data.form.userId = data.user.id
  request.post('/userCertification/add', data.form).then(res => {
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
  request.put('/userCertification/update', data.form).then(res => {
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

const loadAreas = () => {
  request.get('/areas/selectAll').then(res => {
    if (res.code === '200') {
      data.areasList = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}
loadAreas()

const loadCertification = () => {
  request.get('/userCertification/selectByUserId/' + data.user.id).then(res => {
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