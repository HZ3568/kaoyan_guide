<template>
  <div style="width: 72%; margin: 20px auto; min-height: 100vh">
    <!-- 顶部专业信息卡片 -->
    <div class="front-card hero-card" style="margin-bottom: 20px">
      <div class="hero-main">
        <div class="hero-icon-wrap">
          <div class="hero-icon">
            <el-icon :size="40"><Reading /></el-icon>
          </div>
          <div class="hero-badge">{{ data.specialtysInfo.categorysName || '学科门类' }}</div>
        </div>
        <div class="hero-info">
          <div class="hero-title">{{ data.specialtysInfo.name || '专业名称' }}</div>
          <div class="hero-subtitle">
            <span>专业代码：{{ data.specialtysInfo.specialtyNumber || '-' }}</span>
            <span class="divider">|</span>
            <span>所属门类：{{ data.specialtysInfo.categorysName || '-' }}</span>
          </div>
          <div class="hero-tags" v-if="data.specialtysInfo.universityName">
            <el-tag size="small" type="success">{{ data.specialtysInfo.universityName }}</el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="front-card content-card">
      <!-- 简介 -->
      <div class="section-block" v-if="data.specialtysInfo.intro">
        <div class="section-header">
          <div class="section-icon"><el-icon><InfoFilled /></el-icon></div>
          <div>
            <div class="section-title">专业简介</div>
            <div class="section-subtitle">培养目标与专业背景</div>
          </div>
        </div>
        <div class="section-content">
          {{ data.specialtysInfo.intro }}
        </div>
      </div>

      <!-- 培养目标 -->
      <div class="section-block" v-if="data.specialtysInfo.trainingObjective">
        <div class="section-header">
          <div class="section-icon"><el-icon><Aim /></el-icon></div>
          <div>
            <div class="section-title">培养目标</div>
            <div class="section-subtitle">专业人才培养方向</div>
          </div>
        </div>
        <div class="section-content">
          {{ data.specialtysInfo.trainingObjective }}
        </div>
      </div>

      <!-- 主要课程 -->
      <div class="section-block" v-if="data.specialtysInfo.mainCourses">
        <div class="section-header">
          <div class="section-icon"><el-icon><Collection /></el-icon></div>
          <div>
            <div class="section-title">主要课程</div>
            <div class="section-subtitle">专业核心学习内容</div>
          </div>
        </div>
        <div class="section-content">
          <div class="course-tags">
            <span
              v-for="(course, idx) in splitCourses(data.specialtysInfo.mainCourses)"
              :key="idx"
              class="course-tag"
            >
              {{ course }}
            </span>
          </div>
        </div>
      </div>

      <!-- 就业方向 -->
      <div class="section-block" v-if="data.specialtysInfo.employmentDirection">
        <div class="section-header">
          <div class="section-icon"><el-icon><Briefcase /></el-icon></div>
          <div>
            <div class="section-title">就业方向</div>
            <div class="section-subtitle">毕业后的职业发展路径</div>
          </div>
        </div>
        <div class="section-content">
          {{ data.specialtysInfo.employmentDirection }}
        </div>
      </div>

      <!-- 官方来源 -->
      <div class="section-block source-block" v-if="data.specialtysInfo.officialSourceUrl">
        <div class="section-header">
          <div class="section-icon"><el-icon><Link /></el-icon></div>
          <div>
            <div class="section-title">官方来源</div>
            <div class="section-subtitle">权威信息出处</div>
          </div>
        </div>
        <div class="section-content">
          <a :href="data.specialtysInfo.officialSourceUrl" target="_blank" class="source-link">
            {{ data.specialtysInfo.officialSourceUrl }}
            <el-icon class="link-icon"><TopRight /></el-icon>
          </a>
        </div>
      </div>

      <!-- 无数据提示 -->
      <div class="empty-tip" v-if="!hasAnyContent">
        <el-empty description="暂无专业详细介绍内容" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import request from "@/utils/request";
import { ElMessage } from "element-plus";
import { Reading, InfoFilled, Aim, Collection, Briefcase, Link, TopRight } from "@element-plus/icons-vue";

const route = useRoute();
const specialtysId = route.query.id;

const data = reactive({
  user: JSON.parse(localStorage.getItem("xm-user") || "{}"),
  specialtysInfo: {},
});

const hasAnyContent = computed(() => {
  const s = data.specialtysInfo;
  return s?.intro || s?.trainingObjective || s?.mainCourses || s?.employmentDirection || s?.officialSourceUrl;
});

// 逗号/分号/换行分隔课程
const splitCourses = (text) => {
  if (!text) return [];
  return text.split(/[,，;；\n]+/).map(c => c.trim()).filter(Boolean);
};

const loadSpecialtysById = () => {
  request.get("/universitySpecialtys/selectById/" + specialtysId).then((res) => {
    if (res.code === "200") {
      data.specialtysInfo = res.data || {};
    } else {
      // fallback to direct specialty query
      request.get("/specialtys/selectById/" + specialtysId).then((r) => {
        if (r.code === "200") {
          data.specialtysInfo = r.data || {};
        } else {
          ElMessage.error(res.msg || "加载失败");
        }
      });
    }
  });
};

onMounted(() => {
  loadSpecialtysById();
});
</script>

<style scoped>
@import "@/assets/css/view.css";

.hero-card {
  padding: 28px 32px;
  border-radius: 20px;
}

.hero-main {
  display: flex;
  align-items: center;
  gap: 24px;
}

.hero-icon-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.hero-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #49c48d;
  box-shadow: 0 4px 16px rgba(73, 196, 141, 0.2);
}

.hero-badge {
  font-size: 13px;
  color: #49c48d;
  font-weight: 600;
  background: #e8f5e9;
  padding: 4px 14px;
  border-radius: 999px;
  white-space: nowrap;
}

.hero-info {
  flex: 1;
  min-width: 0;
}

.hero-title {
  font-size: 32px;
  font-weight: 800;
  color: #1f2937;
  margin-bottom: 10px;
  line-height: 1.3;
}

.hero-subtitle {
  font-size: 15px;
  color: #6b7280;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.divider {
  color: #d1d5db;
}

.hero-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.content-card {
  padding: 28px 32px;
  border-radius: 20px;
}

.section-block {
  margin-bottom: 36px;
  padding-bottom: 36px;
  border-bottom: 1px solid #f0f0f0;
}

.section-block:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
}

.section-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f0f7f2 0%, #e8f5e9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #49c48d;
  font-size: 20px;
  flex-shrink: 0;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.section-subtitle {
  font-size: 13px;
  color: #9ca3af;
}

.section-content {
  font-size: 15px;
  color: #4b5563;
  line-height: 2;
  padding-left: 58px;
}

.course-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.course-tag {
  padding: 7px 16px;
  background: linear-gradient(135deg, #f0f7f2 0%, #e8f5e9 100%);
  border: 1px solid #c8e6c9;
  border-radius: 999px;
  font-size: 14px;
  color: #374151;
  transition: all 0.2s;
}

.course-tag:hover {
  background: linear-gradient(135deg, #49c48d 0%, #3db87d 100%);
  color: #fff;
  border-color: #49c48d;
}

.source-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #2563eb;
  text-decoration: none;
  font-size: 15px;
  word-break: break-all;
  border-bottom: 1px dashed rgba(37, 99, 235, 0.4);
  padding-bottom: 2px;
  transition: color 0.2s;
}

.source-link:hover {
  color: #1d4ed8;
}

.link-icon {
  font-size: 14px;
}

.empty-tip {
  padding: 40px 0;
}

@media (max-width: 768px) {
  .hero-main {
    flex-direction: column;
    text-align: center;
  }
  .hero-subtitle {
    justify-content: center;
  }
  .hero-tags {
    justify-content: center;
  }
  .section-content {
    padding-left: 0;
  }
  .content-card {
    padding: 20px;
  }
  .hero-title {
    font-size: 24px;
  }
}
</style>
