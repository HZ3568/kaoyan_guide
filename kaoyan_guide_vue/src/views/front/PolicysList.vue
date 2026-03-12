<template>
  <div class="main-content">
    <div style="display: flex; grid-gap: 20px">
      <div style="flex: 1" class="front-card">
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
            招生政策
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

const data = reactive({
  user: JSON.parse(localStorage.getItem("xm-user") || "{}"),
  tableData: [],
  total: 0,
  pageNum: 1, // 当前的页码
  pageSize: 5, // 每页的个数
  policysList: [],
});

// 加载表格数据
const load = () => {
  request
    .get("/policys/selectPage", {
      params: {
        pageNum: data.pageNum,
        pageSize: data.pageSize,
      },
    })
    .then((res) => {
      data.tableData = res.data?.list || [];
      data.total = res.data?.total;
      window.scrollTo({ top: 0 });
    });
};

load();

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
</style>
