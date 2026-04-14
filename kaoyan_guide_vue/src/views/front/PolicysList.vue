<template>
  <div class="main-content">
    <div style="display: flex; grid-gap: 20px">
      <div style="flex: 1" class="front-card">
        <!-- 标题 + 搜索同一行 -->
        <div class="list-header">
          <div class="list-title">
            <img
              alt=""
              src="@/assets/imgs/热门政策.png"
              style="width: 36px; height: 36px"
            />
            <span>招生政策</span>
          </div>
          <div class="list-search">
            <el-input
              v-model="data.searchKey"
              placeholder="搜索政策标题 / 学校名称 / 关键词"
              size="large"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
              class="search-input"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" size="large" @click="handleSearch" class="search-btn">搜索</el-button>
            <el-button size="large" @click="handleReset" class="reset-btn">重置</el-button>
          </div>
        </div>
        <div>
          <div
            v-for="item in data.tableData"
            :key="item.id"
            style="margin-bottom: 20px"
          >
            <div
              style="font-size: 20px; font-weight: bold; cursor: pointer"
              class="line1 policy-title"
              @click="$router.push('/front/policysDetail?id=' + item.id)"
            >
              {{ item.name }}
            </div>
            <div
              style="
                margin-top: 10px;
                line-height: 20px;
                height: 40px;
                color: #666;
              "
              class="line2"
            >
              {{ item.intro }}
            </div>
            <div
              style="
                margin-top: 10px;
                display: flex;
                align-items: center;
                color: #666;
                font-size: 13px;
              "
            >
              <div
                style="display: flex; align-items: center; margin-right: 20px"
              >
                <img
                  :src="item.universityAvatar"
                  alt=""
                  style="
                    width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    margin-right: 5px;
                  "
                />
                <span class="line1">{{ item.universityName }}</span>
              </div>
              <div
                style="display: flex; align-items: center; margin-right: 20px"
              >
                <el-icon><View /></el-icon>
                <span style="margin-left: 5px">{{ item.viewCount }}</span>
              </div>
              <div style="display: flex; align-items: center">
                <el-icon><Clock /></el-icon>
                <span style="margin-left: 5px">{{ item.time }}</span>
              </div>
            </div>
          </div>
          <div style="margin-top: 20px" v-if="data.total">
            <el-pagination
              @current-change="load"
              layout="total, prev, pager, next"
              :page-size="data.pageSize"
              v-model:current-page="data.pageNum"
              :total="data.total"
            />
          </div>
        </div>
      </div>
      <div style="width: 400px" class="front-card">
        <div
          style="
            display: flex;
            grid-gap: 10px;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 2px solid #49c48d;
            margin-bottom: 20px;
          "
        >
          <img
            alt=""
            src="@/assets/imgs/热门政策.png"
            style="width: 40px; height: 40px"
          />
          <div style="flex: 1; font-size: 24px; font-weight: bold">
            热门政策
          </div>
        </div>
        <div>
          <div
            v-for="item in data.policysList"
            :key="item.id"
            style="margin-bottom: 20px"
          >
            <div
              class="line1 policy-title"
              @click="$router.push('/front/policysDetail?id=' + item.id)"
            >
              {{ item.name }}
            </div>
            <div style="display: flex; align-items: center; color: #888">
              <el-icon :size="18"><Clock /></el-icon>
              <span style="color: #8a8a8a; margin-left: 2px">{{
                item.time
              }}</span>
              <el-icon :size="18" style="margin-left: 20px"><View /></el-icon>
              <span style="color: #8a8a8a; margin-left: 2px">{{
                item.viewCount
              }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import request from "@/utils/request";
import { ElMessage } from "element-plus";
import { Search, View, Clock } from "@element-plus/icons-vue";

const data = reactive({
  user: JSON.parse(localStorage.getItem("xm-user") || "{}"),
  tableData: [],
  total: 0,
  pageNum: 1, // 当前的页码
  pageSize: 5, // 每页的个数
  policysList: [],
  searchKey: "",
});

// 加载表格数据
const load = () => {
  request
    .get("/policys/selectPage", {
      params: {
        pageNum: data.pageNum,
        pageSize: data.pageSize,
        name: data.searchKey,
        intro: data.searchKey,
      },
    })
    .then((res) => {
      data.tableData = res.data?.list || [];
      data.total = res.data?.total;
      window.scrollTo({ top: 0 });
    });
};

load();

// 搜索
const handleSearch = () => {
  data.pageNum = 1;
  load();
};

// 重置
const handleReset = () => {
  data.searchKey = "";
  data.pageNum = 1;
  load();
};

// 获取浏览量最多的前10个政策
const loadHotPolicys = () => {
  request.get("/policys/loadHotPolicys").then((res) => {
    if (res.code === "200") {
      data.policysList = res.data;
    } else {
      ElMessage.error(res.msg);
    }
  });
};
loadHotPolicys();
</script>

<style scoped>
.policy-title {
  font-size: 16px;
  color: #000;
  margin-bottom: 10px;
  cursor: pointer;
}
.policy-title:hover {
  color: #49c48d;
  font-weight: bold;
}

/* 标题 + 搜索同一行布局 */
.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding-bottom: 20px;
  border-bottom: 2px solid #49c48d;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.list-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: bold;
  color: #1f2937;
  flex-shrink: 0;
}

.list-search {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
  max-width: 640px;
}

.search-input {
  flex: 1;
  min-width: 0;
}
.search-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  border-color: #c8e6c9;
  font-size: 15px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-input :deep(.el-input__wrapper:hover),
.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #49c48d;
  box-shadow: 0 0 0 3px rgba(73, 196, 141, 0.15);
}

.search-btn {
  border-radius: 8px;
  background: #49c48d;
  border-color: #49c48d;
  font-weight: bold;
  flex-shrink: 0;
}
.search-btn:hover {
  background: #3db87d;
  border-color: #3db87d;
}

.reset-btn {
  border-radius: 8px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .list-header {
    flex-direction: column;
    align-items: stretch;
  }
  .list-title {
    font-size: 20px;
  }
  .list-search {
    max-width: 100%;
  }
}
</style>
