<template>
  <div class="detail-page">
    <!-- 顶部学校信息区域（已去重） -->
    <div class="front-card hero-card">
      <div class="hero-main">
        <!-- 左侧视觉展示区 -->
        <div class="hero-visual">
          <div class="hero-visual-card">
            <div class="hero-kicker">UNIVERSITY</div>

            <div class="logo-shell">
              <img
                :src="data.universityData.avatar"
                alt="学校校徽"
                class="school-logo"
              />
            </div>

            <div class="hero-tags">
              <el-tag
                size="small"
                type="danger"
                v-if="data.universityData.is985"
              >
                985
              </el-tag>
              <el-tag
                size="small"
                type="warning"
                v-if="data.universityData.is211"
              >
                211
              </el-tag>
              <el-tag
                size="small"
                type="success"
                v-if="data.universityData.isDoubleFirstClass"
              >
                双一流
              </el-tag>
            </div>

            <div class="hero-visual-tip">
              院校信息展示
            </div>
          </div>
        </div>

        <!-- 右侧信息区 -->
        <div class="hero-info">
          <div class="hero-title-row">
            <div class="hero-title-wrap">
              <div class="hero-title">
                {{ data.universityData.name || "院校名称" }}
              </div>
              <div class="hero-subtitle">
                院校详情 · 专业信息 · 学校评价参考
              </div>
            </div>
          </div>

          <div class="hero-info-panel">
            <div class="section-label">院校档案</div>

            <div class="info-grid">
              <div class="info-item">
                <span class="info-key">所在地区</span>
                <span class="info-value">
                  {{ data.universityData.provinceName || "-" }}
                </span>
              </div>

              <div class="info-item">
                <span class="info-key">院校类型</span>
                <span class="info-value">
                  {{ data.universityData.schoolType || "-" }}
                </span>
              </div>

              <div class="info-item">
                <span class="info-key">办学层次</span>
                <span class="info-value">
                  {{ data.universityData.educationLevel || "-" }}
                </span>
              </div>

              <div class="info-item">
                <span class="info-key">院校属性</span>
                <span class="info-value">
                  {{ data.universityData.is985 ? "985" : "非985" }} /
                  {{ data.universityData.is211 ? "211" : "非211" }} /
                  {{
                    data.universityData.isDoubleFirstClass ? "双一流" : "非双一流"
                  }}
                </span>
              </div>

              <div class="info-item info-item-full">
                <span class="info-key">详细地址</span>
                <span class="info-value">
                  {{ data.universityData.address || "-" }}
                </span>
              </div>

              <div class="info-item info-item-full">
                <span class="info-key">官方网址</span>
                <span class="info-value">
                  <a
                    v-if="data.universityData.officialWebsite"
                    :href="data.universityData.officialWebsite"
                    target="_blank"
                  >
                    点击访问官网
                  </a>
                  <span v-else>-</span>
                </span>
              </div>
            </div>
          </div>

          <div class="hero-action-row">
            <div
              class="collect-box"
              @click="collectGoods(data.universityData.collectFlag)"
            >
              <el-icon
                class="collect-icon"
                :class="{ active: data.universityData.collectFlag }"
              >
                <Star />
              </el-icon>
              <span :class="{ active: data.universityData.collectFlag }">
                {{ data.universityData.collectFlag ? "取消收藏" : "收藏" }}
              </span>
            </div>

            <el-button
              type="warning"
              @click="showComment"
              :disabled="data.universityData.commentFlag"
            >
              评价学校
            </el-button>

            <span class="tips-text">每人每个学校只能评价一次</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 地图卡片 -->
    <div class="front-card map-card">
      <div class="map-header">
        <div>
          <div class="map-title">学校位置</div>
          <div class="map-subtitle">
            {{ data.universityData.provinceName || "-" }}
            {{ data.universityData.address || "" }}
          </div>
        </div>
      </div>

      <div class="map-wrapper">
        <div
          id="university-map"
          class="map-container"
        ></div>

        <div
          v-if="data.mapLoading"
          class="map-mask"
        >
          地图加载中...
        </div>

        <div
          v-else-if="data.mapError"
          class="map-mask"
        >
          {{ data.mapError }}
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="front-card content-card">
      <div class="category-bar">
        <div
          v-for="item in data.activeCategory"
          :key="item"
          class="category-item"
          :class="{ 'category-active': data.selectType === item }"
          @click="changeCategory(item)"
        >
          {{ item }}
        </div>
      </div>

      <!-- 学校简介 -->
      <div
        v-if="data.selectType === '学校简介'"
        class="content-inner intro-page"
      >
        <div class="intro-header">
          <div class="intro-header-left">
            <div class="intro-kicker">UNIVERSITY PROFILE</div>
            <div class="intro-title">学校简介</div>
            <div class="intro-desc">
              了解 {{ data.universityData.name || "该院校" }} 的基本情况、办学特色与发展概况
            </div>
          </div>
        </div>

        <div class="intro-meta-bar">
          <div class="intro-meta-item">
            <span class="intro-meta-label">院校名称</span>
            <span class="intro-meta-value">{{ data.universityData.name || "-" }}</span>
          </div>
          <div class="intro-meta-item">
            <span class="intro-meta-label">所在地区</span>
            <span class="intro-meta-value">{{ data.universityData.provinceName || "-" }}</span>
          </div>
          <div class="intro-meta-item">
            <span class="intro-meta-label">院校类型</span>
            <span class="intro-meta-value">{{ data.universityData.schoolType || "-" }}</span>
          </div>
          <div class="intro-meta-item">
            <span class="intro-meta-label">办学层次</span>
            <span class="intro-meta-value">{{ data.universityData.educationLevel || "-" }}</span>
          </div>
        </div>

        <div class="intro-article-card">
          <div class="intro-article-head">
            <div class="intro-article-title">院校概况</div>
            <div class="intro-article-line"></div>
          </div>

          <div
            class="rich-content official-rich-content"
            v-html="data.universityData.description || '暂无学校简介'"
          ></div>
        </div>
      </div>

      <!-- 专业介绍 -->
      <div
        v-if="data.selectType === '专业介绍'"
        class="content-inner"
      >
        <div
          v-for="(categorysItem, index) in data.categorysList"
          :key="index"
          class="major-block"
        >
          <div class="major-block-title">
            {{ categorysItem.name }}
          </div>

          <div class="major-list">
            <span
              v-for="specialtysItem in data.specialtysList"
              :key="specialtysItem.id"
            >
              <div
                class="specialtys-active"
                v-if="specialtysItem.categorysId === categorysItem.id"
                @click="
                  $router.push('/front/specialtysDetail?id=' + specialtysItem.id)
                "
              >
                {{ specialtysItem.specialtysName }}
              </div>
            </span>
          </div>
        </div>
      </div>

      <!-- 学校评价 -->
      <div
        v-if="data.selectType === '学校评价'"
        class="comment-area"
      >
        <div
          class="comment-item"
          v-for="item in data.commentList"
          :key="item.id"
        >
          <div class="comment-user">
            <div class="comment-avatar-wrap">
              <img
                :src="item.userAvatar"
                alt=""
                class="comment-avatar"
              />
            </div>

            <div class="comment-meta">
              <div class="comment-name">
                {{ item.userName }}
              </div>
              <div class="comment-time-row">
                <div class="comment-time">
                  {{ item.time }}
                </div>
                <el-rate
                  v-model="item.mark"
                  disabled
                />
              </div>
            </div>
          </div>

          <div class="comment-content">
            {{ item.details }}
          </div>
        </div>
      </div>
    </div>

    <!-- 评价弹窗 -->
    <el-dialog
      title="学校评价"
      v-model="data.formVisible"
      width="40%"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :rules="data.rules"
        :model="data.form"
        label-width="80px"
        style="padding: 20px"
      >
        <el-form-item
          prop="details"
          label="评价内容"
        >
          <el-input
            v-model="data.form.details"
            placeholder="请输入评价内容"
            type="textarea"
            rows="4"
          ></el-input>
        </el-form-item>

        <el-form-item
          prop="mark"
          label="评分"
        >
          <el-rate v-model="data.form.mark" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="data.formVisible = false">取 消</el-button>
          <el-button
            type="primary"
            @click="addComment"
          >
            确 定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, onMounted, ref, nextTick } from "vue";
import request from "@/utils/request";
import { ElMessage } from "element-plus";
import { useRoute } from "vue-router";
import { Star } from "@element-plus/icons-vue";

const route = useRoute();
const formRef = ref();
const universityId = route.query.id;

const data = reactive({
  user: JSON.parse(localStorage.getItem("xm-user") || "{}"),
  universityData: {},
  formVisible: false,
  form: {},
  selectType: "学校简介",
  activeCategory: ["学校简介", "专业介绍", "学校评价"],
  specialtysList: [],
  categorysList: [],
  commentList: [],
  activeCategoryId: null,
  mapLoading: false,
  mapError: "",
  rules: {
    details: [{ required: true, message: "请输入评价内容", trigger: "blur" }],
    mark: [{ required: true, message: "请选择评分", trigger: "blur" }],
  },
});

onMounted(() => {
  loadUniversity();
  loadCategorys();
  loadUniversitySpecialtys();
  loadComment();
});

const loadUniversity = () => {
  request
    .get("/university/selectByUniversityId/" + universityId)
    .then((res) => {
      if (res.code === "200") {
        data.universityData = res.data;
        nextTick(() => {
          initUniversityMap();
        });
      } else {
        ElMessage.error(res.msg);
      }
    });
};

const loadBaiduMap = () => {
  return new Promise((resolve, reject) => {
    if (window.BMapGL && window.BMapGL.Map) {
      resolve(window.BMapGL);
      return;
    }

    const ak = import.meta.env.VITE_BAIDU_MAP_AK;
    if (!ak) {
      reject(new Error("未配置百度地图 AK"));
      return;
    }

    const callbackName = "__bmap_init_cb__";
    window[callbackName] = () => {
      delete window[callbackName];
      resolve(window.BMapGL);
    };

    const existedScript = document.getElementById("baidu-map-script");
    if (existedScript) {
      return;
    }

    const script = document.createElement("script");
    script.id = "baidu-map-script";
    script.src = `https://api.map.baidu.com/api?v=1.0&type=webgl&ak=${ak}&callback=${callbackName}`;
    script.async = true;
    script.onerror = () => reject(new Error("百度地图脚本加载失败"));
    document.head.appendChild(script);
  });
};

const renderMapByPoint = (BMapGL, point) => {
  const container = document.getElementById("university-map");
  if (!container) return;

  container.innerHTML = "";

  const map = new BMapGL.Map("university-map", {
    enableRotate: false,
    enableTilt: false,
  });

  map.centerAndZoom(point, 16);
  map.enableScrollWheelZoom(true);

  const marker = new BMapGL.Marker(point);
  map.addOverlay(marker);

  const name = data.universityData.name || "学校";
  const address = [
    data.universityData.provinceName,
    data.universityData.address,
  ]
    .filter(Boolean)
    .join(" ");

  const infoContent = `<div style="padding:4px 6px;font-size:13px;line-height:1.8">
    <b>${name}</b>${address ? `<br/>${address}` : ""}
  </div>`;

  const infoWindow = new BMapGL.InfoWindow(infoContent, { width: 220 });
  marker.addEventListener("click", () => map.openInfoWindow(infoWindow, point));
  map.openInfoWindow(infoWindow, point);
};

const initUniversityMap = async () => {
  data.mapError = "";
  data.mapLoading = true;

  try {
    const BMapGL = await loadBaiduMap();
    await nextTick();

    const rawLng = data.universityData.longitude;
    const rawLat = data.universityData.latitude;
    const lng = rawLng != null && rawLng !== "" ? Number(rawLng) : NaN;
    const lat = rawLat != null && rawLat !== "" ? Number(rawLat) : NaN;

    if (!Number.isNaN(lng) && !Number.isNaN(lat) && lng !== 0 && lat !== 0) {
      const point = new BMapGL.Point(lng, lat);
      renderMapByPoint(BMapGL, point);
      data.mapLoading = false;
      return;
    }

    const address = `${data.universityData.provinceName || ""}${
      data.universityData.address || ""
    }`.trim();

    if (!address) {
      data.mapLoading = false;
      data.mapError = "暂无学校地址，无法显示地图";
      return;
    }

    const geocoder = new BMapGL.Geocoder();
    geocoder.getPoint(
      address,
      (point) => {
        data.mapLoading = false;

        if (!point) {
          data.mapError = "地址解析失败，请补充更精确的学校地址";
          return;
        }

        renderMapByPoint(BMapGL, point);
      },
      data.universityData.provinceName || ""
    );
  } catch (e) {
    data.mapLoading = false;
    data.mapError = e.message || "地图加载失败";
  }
};

const collectGoods = (flag) => {
  const dataForm = {
    universityId: data.universityData.id,
    userId: data.user.id,
  };

  request.post("/collect/collectUniversity", dataForm).then((res) => {
    if (res.code === "200") {
      loadUniversity();
      if (!flag) {
        ElMessage.success("已收藏");
      } else {
        ElMessage.success("已取消收藏");
      }
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const loadCategorys = () => {
  request.get("/categorys/selectAll").then((res) => {
    if (res.code === "200") {
      data.categorysList = res.data;
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const loadUniversitySpecialtys = () => {
  request
    .get("/universitySpecialtys/selectAll", {
      params: {
        universityId,
      },
    })
    .then((res) => {
      if (res.code === "200") {
        data.specialtysList = res.data;
      } else {
        ElMessage.error(res.msg);
      }
    });
};

const changeCategory = (item) => {
  data.selectType = item;
};

const showComment = () => {
  data.formVisible = true;
};

const addComment = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      data.form.userId = data.user.id;
      data.form.universityId = universityId;
      request.post("/comment/add", data.form).then((res) => {
        if (res.code === "200") {
          data.formVisible = false;
          ElMessage.success("评价成功");
          loadUniversity();
          loadComment();
        } else {
          ElMessage.error(res.msg);
        }
      });
    }
  });
};

const loadComment = () => {
  request
    .get("/comment/selectAll", {
      params: {
        universityId,
      },
    })
    .then((res) => {
      if (res.code === "200") {
        data.commentList = res.data;
      } else {
        ElMessage.error(res.msg);
      }
    });
};
</script>

<style scoped>
.detail-page {
  width: 76%;
  max-width: 1400px;
  margin: 20px auto;
  min-height: 100vh;
}

.hero-card {
  margin-bottom: 20px;
  padding: 26px;
  border-radius: 22px;
}

.hero-main {
  display: flex;
  gap: 24px;
  align-items: stretch;
}

.hero-visual {
  width: 280px;
  flex-shrink: 0;
}

.hero-visual-card {
  height: 100%;
  border-radius: 22px;
  padding: 24px 20px;
  background: linear-gradient(180deg, #f8fbf9 0%, #f2f8f4 100%);
  border: 1px solid #e8f1eb;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.hero-kicker {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.8px;
  color: #49c48d;
  margin-bottom: 18px;
}

.logo-shell {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: #ffffff;
  border: 1px solid #edf1ee;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 8px #f8fbf9;
  margin-bottom: 18px;
}

.school-logo {
  width: 108px;
  height: 108px;
  object-fit: contain;
  display: block;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-bottom: 14px;
}

.hero-visual-tip {
  font-size: 13px;
  color: #7b8794;
  text-align: center;
  line-height: 1.7;
}

.hero-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.hero-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.hero-title-wrap {
  min-width: 0;
}

.hero-title {
  font-size: 36px;
  font-weight: 800;
  color: #1f2937;
  line-height: 1.3;
  margin-bottom: 8px;
  word-break: break-word;
}

.hero-subtitle {
  font-size: 15px;
  color: #6b7280;
  line-height: 1.7;
}

.hero-info-panel {
  background: #fafbfc;
  border-radius: 18px;
  padding: 20px 22px;
  border: 1px solid #f0f2f5;
}

.section-label {
  font-size: 19px;
  font-weight: 700;
  margin-bottom: 16px;
  color: #222;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.info-item-full {
  grid-column: span 2;
}

.info-key {
  font-size: 13px;
  color: #999;
}

.info-value {
  font-size: 15px;
  color: #333;
  word-break: break-all;
  line-height: 1.75;
}

.hero-action-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 18px;
  flex-wrap: wrap;
}

.collect-box {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: none;
  padding: 9px 16px;
  border-radius: 999px;
  background: #fff7f7;
  border: 1px solid #ffe1e1;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.collect-box:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.08);
}

.collect-icon {
  font-size: 18px;
  color: #666;
}

.collect-icon.active,
.collect-box span.active {
  color: #e74c3c;
}

.tips-text {
  color: #f56c6c;
  font-size: 13px;
}

.map-card {
  margin-bottom: 20px;
  padding: 20px;
  border-radius: 18px;
}

.map-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.map-title {
  font-size: 20px;
  font-weight: 700;
  color: #222;
  margin-bottom: 6px;
}

.map-subtitle {
  font-size: 14px;
  color: #888;
  line-height: 1.6;
}

.map-wrapper {
  position: relative;
  width: 100%;
  height: 380px;
  border: 1px solid #eeeeee;
  border-radius: 16px;
  overflow: hidden;
  background: #f8f8f8;
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-mask {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.88);
  z-index: 10;
}

.content-card {
  margin-bottom: 20px;
  border-radius: 18px;
  padding: 20px 24px;
}

.category-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  margin-bottom: 20px;
  border-bottom: 1px solid #f2f2f2;
  padding-bottom: 12px;
}

.category-item {
  font-size: 18px;
  padding-bottom: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-item:hover {
  color: #49c48d;
}

.category-active {
  color: #49c48d;
  border-bottom: 2px solid #49c48d;
  font-weight: bold;
}

.content-inner {
  padding: 10px 8px 16px;
  color: #374151;
  line-height: 1.9;
  font-size: 15px;
}

/* 学校简介官网化排版 */
.intro-page {
  padding: 6px 4px 18px;
}

.intro-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 18px;
}

.intro-header-left {
  min-width: 0;
}

.intro-kicker {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.6px;
  color: #49c48d;
  margin-bottom: 10px;
}

.intro-title {
  font-size: 30px;
  font-weight: 800;
  color: #1f2937;
  line-height: 1.3;
  margin-bottom: 8px;
}

.intro-desc {
  font-size: 15px;
  color: #6b7280;
  line-height: 1.9;
}

.intro-meta-bar {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 22px;
}

.intro-meta-item {
  padding: 16px 18px;
  background: linear-gradient(180deg, #fbfcfd 0%, #f7fafc 100%);
  border: 1px solid #edf2f7;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.intro-meta-label {
  font-size: 12px;
  color: #94a3b8;
}

.intro-meta-value {
  font-size: 16px;
  font-weight: 700;
  color: #334155;
  line-height: 1.6;
  word-break: break-word;
}

.intro-article-card {
  background: #ffffff;
  border: 1px solid #eef2f6;
  border-radius: 20px;
  padding: 24px 26px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
}

.intro-article-head {
  margin-bottom: 18px;
}

.intro-article-title {
  font-size: 22px;
  font-weight: 800;
  color: #1f2937;
  margin-bottom: 10px;
}

.intro-article-line {
  width: 72px;
  height: 4px;
  border-radius: 999px;
  background: linear-gradient(90deg, #49c48d 0%, #9be3bf 100%);
}

.official-rich-content {
  color: #374151;
  font-size: 16px;
  line-height: 2;
}

.official-rich-content :deep(h1),
.official-rich-content :deep(h2),
.official-rich-content :deep(h3),
.official-rich-content :deep(h4),
.official-rich-content :deep(h5) {
  color: #1f2937;
  font-weight: 800;
  line-height: 1.5;
  margin: 28px 0 14px;
  position: relative;
}

.official-rich-content :deep(h1) {
  font-size: 28px;
}

.official-rich-content :deep(h2) {
  font-size: 24px;
  padding-left: 14px;
}

.official-rich-content :deep(h2::before) {
  content: "";
  position: absolute;
  left: 0;
  top: 0.35em;
  width: 5px;
  height: 1.1em;
  border-radius: 999px;
  background: #49c48d;
}

.official-rich-content :deep(h3) {
  font-size: 20px;
}

.official-rich-content :deep(h4) {
  font-size: 18px;
}

.official-rich-content :deep(p) {
  margin: 14px 0;
  color: #4b5563;
  text-align: justify;
  line-height: 2;
  text-indent: 2em;
}

.official-rich-content :deep(strong),
.official-rich-content :deep(b) {
  color: #1f2937;
  font-weight: 700;
}

.official-rich-content :deep(ul),
.official-rich-content :deep(ol) {
  margin: 14px 0 14px 22px;
  padding: 0;
  color: #4b5563;
}

.official-rich-content :deep(li) {
  margin: 10px 0;
  line-height: 1.9;
}

.official-rich-content :deep(blockquote) {
  margin: 18px 0;
  padding: 16px 18px;
  background: #f8fafc;
  border-left: 4px solid #49c48d;
  border-radius: 12px;
  color: #475569;
}

.official-rich-content :deep(a) {
  color: #2563eb;
  text-decoration: none;
  border-bottom: 1px dashed rgba(37, 99, 235, 0.35);
}

.official-rich-content :deep(a:hover) {
  color: #1d4ed8;
}

.official-rich-content :deep(img) {
  display: block;
  max-width: 100%;
  margin: 18px auto;
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

.official-rich-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 18px 0;
  overflow: hidden;
  border-radius: 14px;
  background: #fff;
}

.official-rich-content :deep(table th) {
  background: #f8fafc;
  color: #1f2937;
  font-weight: 700;
}

.official-rich-content :deep(table td),
.official-rich-content :deep(table th) {
  border: 1px solid #e5e7eb;
  padding: 12px 14px;
  line-height: 1.8;
  text-align: left;
}

.official-rich-content :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 24px 0;
}

.major-block {
  margin-bottom: 24px;
}

.major-block-title {
  width: fit-content;
  padding-bottom: 10px;
  border-bottom: 3px solid #49c48d;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 14px;
}

.major-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px 16px;
}

.specialtys-active {
  padding: 8px 14px;
  border-radius: 999px;
  background: #f7faf8;
  border: 1px solid #e8f3ed;
  cursor: pointer;
  color: #444;
  transition: all 0.2s ease;
}

.specialtys-active:hover {
  color: #49c48d;
  border-color: #49c48d;
  background: #f1fcf6;
}

.comment-area {
  padding: 10px 4px;
}

.comment-item {
  padding: 18px 0;
  border-bottom: 1px solid #f2f2f2;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-user {
  display: flex;
  align-items: flex-start;
}

.comment-avatar-wrap {
  width: 44px;
  flex-shrink: 0;
}

.comment-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
}

.comment-meta {
  margin-left: 12px;
}

.comment-name {
  font-weight: 700;
  font-size: 16px;
  color: #222;
  margin-bottom: 6px;
}

.comment-time-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.comment-time {
  color: #7a7a7a;
  font-size: 13px;
}

.comment-content {
  margin-top: 14px;
  font-size: 15px;
  line-height: 1.8;
  color: #333;
}

@media (max-width: 1200px) {
  .detail-page {
    width: 90%;
  }

  .hero-main {
    flex-direction: column;
  }

  .hero-visual {
    width: 100%;
  }

  .hero-visual-card {
    padding: 22px 18px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .info-item-full {
    grid-column: span 1;
  }

  .intro-meta-bar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .map-wrapper {
    height: 320px;
  }

  .category-bar {
    gap: 24px;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .detail-page {
    width: 94%;
  }

  .hero-card,
  .content-card,
  .map-card {
    padding: 16px;
  }

  .hero-title {
    font-size: 28px;
  }

  .logo-shell {
    width: 140px;
    height: 140px;
  }

  .school-logo {
    width: 92px;
    height: 92px;
  }

  .intro-title {
    font-size: 24px;
  }

  .intro-meta-bar {
    grid-template-columns: 1fr;
  }

  .intro-article-card {
    padding: 18px 16px;
  }

  .official-rich-content {
    font-size: 15px;
    line-height: 1.9;
  }

  .official-rich-content :deep(p) {
    text-indent: 0;
  }

  .official-rich-content :deep(h1) {
    font-size: 24px;
  }

  .official-rich-content :deep(h2) {
    font-size: 21px;
  }

  .official-rich-content :deep(h3) {
    font-size: 18px;
  }

  .map-wrapper {
    height: 280px;
  }
}
</style>