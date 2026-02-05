<template>
  <div style="width: 60%; margin: 20px auto; min-height: 100vh">
    <div
      style="
        border: 1px solid #eeeeee;
        padding: 15px 30px;
        border-radius: 5px;
        margin-bottom: 20px;
      "
    >
      <div style="display: flex">
        <el-input
          v-model="data.name"
          placeholder="请输入学校名称查询"
          style="width: 400px; height: 40px"
          clearable
          @clear="load"
          @keyup.enter="load"
        ></el-input>
        <el-button
          type="info"
          plain
          style="margin-left: 10px; height: 40px; width: 100px"
          @click="load"
          >查询</el-button
        >
      </div>
      <div
        style="
          display: flex;
          align-items: center;
          border-bottom: 1px solid #eeeeee;
          padding: 10px 0;
        "
      >
        <div style="width: 90px">院校所在地：</div>
        <div style="flex: 1">
          <div style="display: flex; align-items: center; flex-wrap: wrap">
            <div
              @click="changeAreasFlag(null)"
              style="
                padding-bottom: 5px;
                margin-right: 20px;
                cursor: pointer;
                margin-bottom: 10px;
              "
              :class="{ 'category-active': data.areasFlag === null }"
            >
              全部
            </div>
            <div
              @click="changeAreasFlag(item.id)"
              style="
                padding-bottom: 5px;
                margin-right: 20px;
                cursor: pointer;
                margin-bottom: 10px;
              "
              :class="{ 'category-active': data.areasFlag === item.id }"
              v-for="item in data.areasData"
              :key="item.id"
            >
              {{ item.name }}
            </div>
          </div>
        </div>
      </div>

      <div style="display: flex; align-items: center; padding: 10px 0">
        <div style="width: 90px">主管部门：</div>
        <div style="flex: 1">
          <div style="display: flex; align-items: center; flex-wrap: wrap">
            <div
              @click="changeDepartmentFlag(null)"
              class="category-item"
              :class="{ 'category-active': data.departmentFlag === null }"
            >
              全部
            </div>
            <div
              @click="changeDepartmentFlag(item)"
              class="category-item"
              :class="{ 'category-active': data.departmentFlag === item }"
              v-for="item in data.departmentData"
              :key="item"
            >
              {{ item }}
            </div>
          </div>
        </div>
      </div>
      <div style="display: flex; align-items: center; padding: 10px 0">
        <div style="width: 90px">办学层次：</div>
        <div style="flex: 1">
          <div style="display: flex; align-items: center; flex-wrap: wrap">
            <div
              @click="changeLevelFlag(null)"
              class="category-item"
              :class="{ 'category-active': data.levelFlag === null }"
            >
              全部
            </div>
            <div
              @click="changeLevelFlag(item)"
              class="category-item"
              :class="{ 'category-active': data.levelFlag === item }"
              v-for="item in data.levelData"
              :key="item"
            >
              {{ item }}
            </div>
          </div>
        </div>
      </div>
      <div
        style="
          display: flex;
          align-items: center;
          border-bottom: 1px solid #eeeeee;
          padding: 10px 0;
        "
      >
        <div style="width: 90px">院校特性：</div>
        <div style="flex: 1">
          <div style="display: flex; align-items: center">
            <div
              @click="changeCharacterFlag(null)"
              class="category-item"
              :class="{ 'category-active': data.characterFlag === null }"
            >
              全部
            </div>
            <div
              @click="changeCharacterFlag(item)"
              class="category-item"
              :class="{ 'category-active': data.characterFlag === item }"
              v-for="item in data.characterData"
              :key="item"
            >
              {{ item }}
            </div>
          </div>
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
              <div
                style="display: flex; align-items: center; margin-bottom: 10px"
              >
                满意度：<el-rate
                  v-model="item.mark"
                  disabled
                  show-score
                  text-color="#ff9900"
                  score-template="满意度{value}"
                />
              </div>
              <div style="margin-bottom: 10px">
                主管部门：{{ item.department }}
              </div>
              <div>地区：{{ item.areasName }}</div>
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
import { reactive, ref } from "vue";
import request from "@/utils/request.js";
import { ElMessage } from "element-plus";
import router from "@/router/index.js";

const data = reactive({
  departmentFlag: null,
  areasFlag: null,
  levelFlag: null,
  characterFlag: null,
  name: null,
  departmentData: ["教育部", "其他部委", "地方", "军校"],
  areasData: [],
  levelData: ["本科", "高职(专科)"],
  characterData: [
    "“双一流”建设高校",
    "民办高校",
    "独立学院",
    "中外合作办学",
    "内地与港澳台地区合作办学",
  ],
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
        department: data.departmentFlag,
        areasId: data.areasFlag,
        level: data.levelFlag,
        characters: data.characterFlag,
        name: data.name,
        status: "审核通过",
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

const changeDepartmentFlag = (id) => {
  data.departmentFlag = id;
  load();
};
const changeAreasFlag = (id) => {
  data.areasFlag = id;
  load();
};
const changeLevelFlag = (id) => {
  data.levelFlag = id;
  load();
};

const changeCharacterFlag = (id) => {
  data.characterFlag = id;
  load();
};
loadAreas();
load();
</script>

<style scoped>
.category-active {
  color: #006cff;
  border-bottom: 2px solid #006cff;
}
</style>