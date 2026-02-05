<template>
  <div class="main-content">
    <div style="display: flex; grid-gap: 10px; margin-bottom: 40px">
      <div style="width: 250px;" class="card">
        <div style="font-size: 22px; font-weight: bold; margin-bottom: 20px"><img alt="" src="@/assets/imgs/快速入口.png" style="width: 20px; height: 20px; margin-right: 10px"> 快速入口</div>
        <div style="display: flex; grid-gap: 10px; align-items: center; margin-bottom: 20px; cursor: pointer" @click="$router.push('/front/addApply')">
          <div style="flex: 1; font-size: 16px">志愿填报</div><el-icon style="font-size: 16px"><ArrowRight /></el-icon>
        </div>
        <div style="display: flex; grid-gap: 10px; align-items: center; margin-bottom: 20px; cursor: pointer" @click="$router.push('/front/universityList')">
          <div style="flex: 1; font-size: 16px">查询院校</div><el-icon style="font-size: 16px"><ArrowRight /></el-icon>
        </div>
        <div style="display: flex; grid-gap: 10px; align-items: center; margin-bottom: 20px; cursor: pointer" @click="$router.push('/front/interpretationsList')">
          <div style="flex: 1; font-size: 16px">专业解读</div><el-icon style="font-size: 16px"><ArrowRight /></el-icon>
        </div>
        <div style="display: flex; grid-gap: 10px; align-items: center; margin-bottom: 20px; cursor: pointer" @click="$router.push('/front/newsList')">
          <div style="flex: 1; font-size: 16px">高考资讯</div><el-icon style="font-size: 16px"><ArrowRight /></el-icon>
        </div>
        <div style="display: flex; grid-gap: 10px; align-items: center; margin-bottom: 20px; cursor: pointer" @click="$router.push('/front/policysList')">
          <div style="flex: 1; font-size: 16px">招生政策</div><el-icon style="font-size: 16px"><ArrowRight /></el-icon>
        </div>
        <div style="display: flex; grid-gap: 10px; align-items: center; cursor: pointer" @click="$router.push('/front/certification')">
          <div style="flex: 1; font-size: 16px">学籍认证</div><el-icon style="font-size: 16px"><ArrowRight /></el-icon>
        </div>
      </div>
      <div style="flex: 1;">
        <!--    首页轮播图-->
        <el-carousel :interval="4000" height="320px">
          <el-carousel-item @click="$router.push('/front/universityDetail?id=' + item.universityId)" v-for="item in data.slideshowList" :key="item.id">
            <img :src="item.img" alt="" style="width: 100%; height: 320px">
          </el-carousel-item>
        </el-carousel>
      </div>
      <div style="width: 250px" class="card">
        <div style="font-size: 22px; font-weight: bold; margin-bottom: 20px"><img alt="" src="@/assets/imgs/最新公告.png" style="width: 20px; height: 20px; margin-right: 10px"> 最新公告</div>
        <div v-for="item in data.noticeList" :key="item.id" style="margin-bottom: 15px" @click="$router.push('/front/noticeList')">
          <div style="font-size: 16px; margin-bottom: 5px; cursor: pointer" class="line1">{{ item.title }}</div>
          <div style="color: #888;">{{ item.time }}</div>
        </div>
      </div>
    </div>
    <div style="margin-bottom: 40px">
      <div style="display: flex; grid-gap: 10px; align-items: end; margin-bottom: 30px">
        <div style="flex: 1; ">
          <span style="font-size: 24px; font-weight: bold;">热门学校</span>
          <span style="margin-left: 10px; color: #8c939d">看看大家都喜欢那个学校吧</span>
        </div>
        <div style="color: #666666; cursor: pointer" @click="$router.push('/front/universityList')">更多>></div>
      </div>
      <div>
        <el-row :gutter="20">
          <el-col :span="12" v-for="item in data.universityList" :key="item.id" >
            <div class="card" style="margin-bottom: 20px; cursor: pointer; display: flex; grid-gap: 20px; align-items: center" @click="$router.push('/front/universityDetail?id=' + item.id)">
              <img alt="" :src="item.avatar" style="width: 100px; height: 100px; border-radius: 50%">
              <div style="flex: 1">
                <div class="line1" style="font-size: 20px; font-weight: bold; margin-bottom: 10px">{{item.name}}</div>
                <div style="display: flex; align-items: center; margin-bottom: 10px">满意度：<el-rate v-model="item.mark" disabled show-score text-color="#ff9900" score-template="满意度{value}"/></div>
                <div style="margin-bottom: 10px">主管部门：{{item.department}}</div>
                <div>地区：{{item.areasName}}</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>

    <div style="margin-bottom: 40px">
      <div style="display: flex; grid-gap: 10px; align-items: end; margin-bottom: 30px">
        <div style="flex: 1; ">
          <span style="font-size: 24px; font-weight: bold;">热门解读</span>
          <span style="margin-left: 10px; color: #8c939d">看看大家都喜欢那个专业吧</span>
        </div>
        <div style="color: #666666; cursor: pointer" @click="$router.push('/front/interpretationsList')">更多>></div>
      </div>
      <div>
        <el-row :gutter="15">
          <el-col :span="8" v-for="item in data.interpretationsList" style="margin-bottom: 20px">
            <div class="card" style="padding: 0; cursor: pointer" @click="$router.push('/front/interpretationsDetail?id=' + item.id)">
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
    </div>

    <div>
      <div style="display: flex; grid-gap: 10px; align-items: end; margin-bottom: 30px">
        <div style="flex: 1; ">
          <span style="font-size: 24px; font-weight: bold;">热门资讯</span>
          <span style="margin-left: 10px; color: #8c939d">看看最近有什么热门资讯吧</span>
        </div>
        <div style="color: #666666; cursor: pointer" @click="$router.push('/front/newsList')">更多>></div>
      </div>
      <el-row :gutter="20">
        <el-col :span="12" v-for="(item,index) in data.newsList" :key="item.id">
          <div v-if="index % 2 === 0" style="display: flex; grid-gap: 20px; cursor: pointer; margin-bottom: 20px" class="card" @click="$router.push('/front/newsDetail?id=' + item.id)">
            <img style="width: 150px; height: 100px; border-radius: 5px; cursor: pointer" :src="item.img" alt="" />
            <div style="flex: 1; width: 0">
              <div style="font-size: 16px; font-weight: bold" class="line1">{{ item.name }}</div>
              <div style="margin-top: 10px; line-height: 20px; height: 40px; color: #666" class="line2">{{ item.intro }}</div>
              <div style="margin-top: 10px; display: flex; align-items: center; color: #666; font-size: 13px">
                <div style="display: flex; align-items: center; margin-right: 20px">
                  <el-icon size="16"><View /></el-icon>
                  <span style="margin-left: 5px">{{ item.viewCount }}</span>
                </div>
                <div style="display: flex; align-items: center; margin-right: 20px">
                  <el-icon size="16"><Clock /></el-icon>
                  <span style="margin-left: 5px">{{ item.time }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else style="display: flex; grid-gap: 20px; cursor: pointer; margin-bottom: 20px" class="card" @click="$router.push('/front/newsDetail?id=' + item.id)">

            <div style="flex: 1; width: 0">
              <div style="font-size: 16px; font-weight: bold" class="line1">{{ item.name }}</div>
              <div style="margin-top: 10px; line-height: 20px; height: 40px; color: #666" class="line2">{{ item.intro }}</div>
              <div style="margin-top: 10px; display: flex; align-items: center; color: #666; font-size: 13px">
                <div style="display: flex; align-items: center; margin-right: 20px">
                  <el-icon size="16"><View /></el-icon>
                  <span style="margin-left: 5px">{{ item.viewCount }}</span>
                </div>
                <div style="display: flex; align-items: center; margin-right: 20px">
                  <el-icon size="16"><Clock /></el-icon>
                  <span style="margin-left: 5px">{{ item.time }}</span>
                </div>
              </div>
            </div>
            <img style="width: 150px; height: 100px; border-radius: 5px; cursor: pointer" :src="item.img" alt="" />
          </div>
        </el-col>
      </el-row>

    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import request from "@/utils/request.js";
import {ElMessage} from "element-plus";


const data = reactive({
  user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
  slideshowList: [],
  noticeList: [],
  universityList: [],
  interpretationsList: [],
  newsList: []
})
// 获取首页轮播图
const loadSlideshow = () => {
  request.get( '/slideshow/selectAll').then(res => {
    if (res.code === '200') {
      data.slideshowList = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}
loadSlideshow()

// 获取最新公告
const loadNotice = () => {
  request.get( '/notice/selectAll').then(res => {
    if (res.code === '200') {
      data.noticeList = res.data.splice(0,4)
    } else {
      ElMessage.error(res.msg)
    }
  })
}
loadNotice()

// 满意度最高的前6的个学校
const loadHotUniversity = () => {
  request.get( '/university/loadHotUniversity').then(res => {
    if (res.code === '200') {
      data.universityList = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}
loadHotUniversity()

// 浏览量前6的专业解读
const loadHotInterpretations = () => {
  request.get( '/interpretations/loadHotInterpretations').then(res => {
    if (res.code === '200') {
      data.interpretationsList = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}
loadHotInterpretations()

// 浏览量前6的资讯信息
const loadHotNews = () => {
  request.get( '/news/loadHotNews').then(res => {
    if (res.code === '200') {
      data.newsList = res.data
    } else {
      ElMessage.error(res.msg)
    }
  })
}
loadHotNews()
</script>