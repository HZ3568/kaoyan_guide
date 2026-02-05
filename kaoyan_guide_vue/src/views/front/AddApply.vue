<template>
  <div style="width: 50%; margin: 20px auto; min-height: 100vh">
    <div class="front-card">
      <div style="text-align: center; color: red; font-size: 18px; font-weight: bold">只有学籍认证通过的才能填报志愿，每个人只能填写一次，请谨慎填报</div>
      <el-form ref="formRef" :rules="data.rules" :model="data.form" label-width="110px" style="padding: 20px">
        <el-form-item prop="firstUniversityId" label="第一志愿大学">
          <el-select v-model="data.form.firstUniversityId" filterable style="width: 100%;" placeholder="请选择第一志愿大学" :disabled="data.form.id !== undefined" @change="loadFirstSpecialtys(null)">
            <el-option :label="item.name" :value="item.id" v-for="item in data.universityList"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="firstSpecialtysId" label="第一志愿专业">
          <el-select v-model="data.form.firstSpecialtysId" filterable style="width: 100%;" placeholder="请选择第一志愿专业" :disabled="data.form.id !== undefined || data.form.firstUniversityId === undefined">
            <el-option :label="item.specialtysName" :value="item.specialtysId" v-for="item in data.firstSpecialtyList"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="secondUniversityId" label="第二志愿大学">
          <el-select v-model="data.form.secondUniversityId" filterable style="width: 100%;" placeholder="请选择第二志愿大学" :disabled="data.form.id !== undefined" @change="loadSecondSpecialtys(null)">
            <el-option :label="item.name" :value="item.id" v-for="item in data.universityList"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="secondSpecialtysId" label="第二志愿专业">
          <el-select v-model="data.form.secondSpecialtysId" filterable style="width: 100%;" placeholder="请选择第二志愿专业" :disabled="data.form.id !== undefined || data.form.secondUniversityId === undefined">
            <el-option :label="item.specialtysName" :value="item.specialtysId" v-for="item in data.secondSpecialtyList"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="thirdUniversityId" label="第三志愿大学">
          <el-select v-model="data.form.thirdUniversityId" filterable style="width: 100%;" placeholder="请选择第三志愿大学" :disabled="data.form.id !== undefined" @change="loadThirdSpecialtys(null)">
            <el-option :label="item.name" :value="item.id" v-for="item in data.universityList"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="thirdSpecialtysId" label="第三志愿专业">
          <el-select v-model="data.form.thirdSpecialtysId" filterable style="width: 100%;" placeholder="请选择第三志愿专业" :disabled="data.form.id !== undefined || data.form.thirdUniversityId === undefined">
            <el-option :label="item.specialtysName" :value="item.specialtysId" v-for="item in data.thirdSpecialtyList"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="status" label="录取状态">
          <el-tag type="warning" style="background-color: orange; color: white" v-if="data.form.id === undefined">待提交</el-tag>
          <el-tag type="warning" v-if="data.form.status === '待录取'">待录取</el-tag>
          <el-tag type="success" v-if="data.form.status === '已录取'">已录取</el-tag>
          <el-tag type="danger" v-if="data.form.status === '未录取'">未录取</el-tag>
        </el-form-item>
        <el-form-item prop="refuseReason" label="拒绝理由" v-if="data.form.status === '审核拒绝'">
          <div style="color: red;">{{data.form.refuseReason}}</div>
        </el-form-item>
        <div style="text-align: center">
          <el-button type="primary" @click="add" :disabled="(data.user.status !== '审核通过') || data.form.id !== undefined">提 交</el-button>
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
  universityList: [],
  firstSpecialtyList: [],
  secondSpecialtyList: [],
  thirdSpecialtyList: [],
  rules: {
    firstUniversityId: [
      { required: true, message: '请选择第一志愿大学', trigger: 'blur' },
    ],
    firstSpecialtysId: [
      { required: true, message: '请选择第一志愿专业', trigger: 'blur' },
    ],
    secondUniversityId: [
      { required: true, message: '请选择第二志愿大学', trigger: 'blur' },
    ],
    secondSpecialtysId: [
      { required: true, message: '请选择第二志愿专业', trigger: 'blur' },
    ],
    thirdUniversityId: [
      { required: true, message: '请选择第三志愿大学', trigger: 'blur' },
    ],
    thirdSpecialtysId: [
      { required: true, message: '请选择第三志愿专业', trigger: 'blur' },
    ],
  },
})
onMounted(()=>{
  loadApply()
  loadUniversity()
})

const loadUniversity = () => {
  request.get('/university/selectAll', {
    params: {
      status: "审核通过",
    }
  }).then(res => {
    if (res.code === '200') {
      data.universityList = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}

// 获取第一志愿大学的所有专业
const loadFirstSpecialtys = (id) => {
  let universityId = null
  if (id === null) {
    universityId = data.form.firstUniversityId
    data.form.firstSpecialtysId = null
  } else {
    universityId = id
  }

  request.get('/universitySpecialtys/selectAll', {
    params: {
      universityId: universityId
    }
  }).then(res => {
    if (res.code === '200') {
      data.firstSpecialtyList = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}

// 获取第二志愿大学的所有专业
const loadSecondSpecialtys = (id) => {
  let universityId = null
  if (id === null) {
    universityId = data.form.secondUniversityId
    if (data.form.firstUniversityId === data.form.secondUniversityId) {
      ElMessage.warning("第一志愿和第二志愿学校不能一样")
      data.form.secondUniversityId = null
      return
    }
    data.form.secondSpecialtysId = null
  } else {
    universityId = id
  }

  request.get('/universitySpecialtys/selectAll', {
    params: {
      universityId: universityId
    }
  }).then(res => {
    if (res.code === '200') {
      data.secondSpecialtyList = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}

// 获取第三志愿大学的所有专业
const loadThirdSpecialtys = (id) => {
  let universityId = null
  if (id === null) {
    universityId = data.form.thirdUniversityId
    if (data.form.firstUniversityId === data.form.thirdUniversityId) {
      ElMessage.warning("第一志愿和第三志愿学校不能一样")
      data.form.thirdUniversityId = null
      return
    }
    if (data.form.secondUniversityId === data.form.thirdUniversityId) {
      ElMessage.warning("第二志愿和第三志愿学校不能一样")
      data.form.thirdUniversityId = null
      return
    }
    data.form.thirdSpecialtysId = null
  } else {
    universityId = id
  }


  request.get('/universitySpecialtys/selectAll', {
    params: {
      universityId: universityId
    }
  }).then(res => {
    if (res.code === '200') {
      data.thirdSpecialtyList = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}
// 新增
const add = () => {
  formRef.value.validate(valid => {
    if (valid) {
      data.form.userId = data.user.id
      request.post('/apply/add', data.form).then(res => {
        if (res.code === '200') {
          ElMessage.success('填报成功')
          loadApply()
        } else {
          ElMessage.error(res.msg)
        }
      })
    }
  })

}


const loadApply = () => {
  request.get('/apply/selectByUserId/' + data.user.id).then(res => {
    if (res.code === '200') {
      data.form = res.data || {}
      if (data.form !== {}) {
        loadFirstSpecialtys(data.form.firstUniversityId)
        loadSecondSpecialtys(data.form.secondUniversityId)
        loadThirdSpecialtys(data.form.thirdUniversityId)
      }
    } else {
      ElMessage.error(res.msg)
    }
  })
}
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