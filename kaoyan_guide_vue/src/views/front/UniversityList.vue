<template>
  <div style="width: 60%; margin: 20px auto; min-height: 100vh">
    <div
      style="
        border: 1px solid #eeeeee;
        padding: 20px 24px;
        border-radius: 8px;
        margin-bottom: 20px;
      "
    >
      <div
        style="
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 12px;
        "
      >
        <el-input
          v-model="data.name"
          placeholder="学校名称"
          clearable
          @keyup.enter="load"
        />
        <el-select
          v-model="data.provinceId"
          placeholder="省份"
          clearable
          filterable
        >
          <el-option
            v-for="item in data.areasData"
            :key="'p' + item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
        <el-select v-model="data.schoolType" placeholder="院校类型" clearable>
          <el-option
            v-for="item in data.schoolTypeOptions"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <el-select
          v-model="data.educationLevel"
          placeholder="办学层次"
          clearable
        >
          <el-option
            v-for="item in data.educationLevelOptions"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <el-select v-model="data.is985" placeholder="985" clearable>
          <el-option label="是" :value="1" />
          <el-option label="否" :value="0" />
        </el-select>
        <el-select v-model="data.is211" placeholder="211" clearable>
          <el-option label="是" :value="1" />
          <el-option label="否" :value="0" />
        </el-select>
        <el-select
          v-model="data.isDoubleFirstClass"
          placeholder="双一流"
          clearable
        >
          <el-option label="是" :value="1" />
          <el-option label="否" :value="0" />
        </el-select>
        <div style="display: flex; gap: 8px">
          <el-button type="primary" @click="load">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </div>
      </div>
    </div>
    <div>
      <el-row :gutter="20">
        <el-col :span="12" v-for="item in data.tableData" :key="item.id">
          <div
            class="card"
            style="
              margin-bottom: 20px;
              cursor: pointer;
              display: flex;
              grid-gap: 20px;
              align-items: center;
            "
            @click="$router.push('/front/universityDetail?id=' + item.id)"
          >
            <img
              alt=""
              :src="item.avatar"
              style="width: 100px; height: 100px; border-radius: 50%"
            />
            <div style="flex: 1">
              <div
                class="line1"
                style="font-size: 20px; font-weight: bold; margin-bottom: 10px"
              >
                {{ item.name }}
              </div>
              <div style="margin-bottom: 8px">
                <el-tag size="small" type="danger" v-if="item.is985"
                  >985</el-tag
                >
                <el-tag
                  size="small"
                  type="warning"
                  v-if="item.is211"
                  style="margin-left: 6px"
                  >211</el-tag
                >
                <el-tag
                  size="small"
                  type="success"
                  v-if="item.isDoubleFirstClass"
                  style="margin-left: 6px"
                  >双一流</el-tag
                >
              </div>
              <div style="margin-bottom: 6px">
                省份：{{ item.provinceName || "-" }}
              </div>
              <div style="margin-bottom: 6px">
                详细地址：{{ item.address || "-" }}
              </div>
              <div style="margin-bottom: 6px">
                院校类型：{{ item.schoolType || "-" }}
              </div>
              <div style="margin-bottom: 6px">
                办学层次：{{ item.educationLevel || "-" }}
              </div>
              <div style="margin-bottom: 6px">
                官网：
                <a
                  v-if="item.officialWebsite"
                  :href="item.officialWebsite"
                  target="_blank"
                  @click.stop
                  >{{ item.officialWebsite }}</a
                >
                <span v-else>-</span>
              </div>
              <div style="margin-bottom: 6px; color: #999">
                更新时间：{{ item.updateTime || "-" }}
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
    <div v-if="data.total">
      <el-pagination
        @current-change="load"
        layout="total, prev, pager, next"
        :page-size="data.pageSize"
        v-model:current-page="data.pageNum"
        :total="data.total"
      />
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import request from "@/utils/request.js";
import { ElMessage } from "element-plus";

const data = reactive({
  provinceId: null,
  schoolType: null,
  educationLevel: null,
  is985: null,
  is211: null,
  isDoubleFirstClass: null,
  name: null,
  areasData: [],
  schoolTypeOptions: [
    "综合类",
    "理工类",
    "师范类",
    "财经类",
    "医药类",
    "农林类",
    "政法类",
    "艺术类",
    "语言类",
    "体育类",
  ],
  educationLevelOptions: ["本科", "专科"],
  pageNum: 1,
  pageSize: 8,
  total: 0,
  tableData: [],
});
const load = () => {
  request
    .get("/university/selectPage", {
      params: {
        pageNum: data.pageNum,
        pageSize: data.pageSize,
        name: data.name,
        provinceId: data.provinceId,
        schoolType: data.schoolType,
        educationLevel: data.educationLevel,
        is985: data.is985,
        is211: data.is211,
        isDoubleFirstClass: data.isDoubleFirstClass,
      },
    })
    .then((res) => {
      if (res.code === "200") {
        data.tableData = res.data.list;
        data.total = res.data.total;
      } else {
        ElMessage.error(res.msg);
      }
    });
};
const loadAreas = () => {
  request.get("/areas/selectAll").then((res) => {
    if (res.code === "200") {
      data.areasData = res.data;
    } else {
      ElMessage.error(res.msg);
    }
  });
};
const reset = () => {
  data.name = null;
  data.provinceId = null;
  data.schoolType = null;
  data.educationLevel = null;
  data.is985 = null;
  data.is211 = null;
  data.isDoubleFirstClass = null;
  data.pageNum = 1;
  load();
};
loadAreas();
load();
</script>
<style scoped></style>
