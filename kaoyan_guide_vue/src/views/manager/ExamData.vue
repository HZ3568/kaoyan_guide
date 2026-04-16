<template>
  <div>
    <div class="card" style="margin-bottom: 5px">
      <el-input
        v-model="data.userName"
        style="width: 200px; margin-right: 10px"
        placeholder="用户名"
        clearable
      />
      <el-select
        v-model="data.subject"
        clearable
        placeholder="科目"
        style="width: 120px; margin-right: 10px"
      >
        <el-option v-for="item in data.subjectOptions" :key="item" :label="item" :value="item" />
      </el-select>
      <el-select
        v-model="data.simulationMode"
        clearable
        placeholder="模拟模式"
        style="width: 160px; margin-right: 10px"
      >
        <el-option label="演示模式" value="演示模式" />
        <el-option label="正式模式" value="正式模式" />
        <el-option label="练习模式" value="练习模式" />
      </el-select>
      <el-button type="info" plain @click="load">查询</el-button>
      <el-button type="warning" plain style="margin: 0 10px" @click="reset">重置</el-button>
      <el-button type="success" plain @click="handleExport">导出 Excel</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px">
      <el-table stripe :data="data.tableData">
        <el-table-column prop="userId" label="用户ID" width="100" />
        <el-table-column prop="userName" label="用户名" width="120" />
        <el-table-column prop="subject" label="科目" width="100" />
        <el-table-column prop="questionSource" label="试题出处" min-width="140" show-overflow-tooltip />
        <el-table-column prop="score" label="成绩" width="80">
          <template #default="scope">
            <span style="font-weight: 600; color: #409eff">{{ scope.row.score }}分</span>
          </template>
        </el-table-column>
        <el-table-column prop="durationSeconds" label="用时(秒)" width="100">
          <template #default="scope">
            {{ formatDuration(scope.row.durationSeconds) }}
          </template>
        </el-table-column>
        <el-table-column prop="simulationMode" label="模拟模式" width="120" />
        <el-table-column prop="createTime" label="提交时间" width="180" />
      </el-table>
    </div>

    <div class="card" v-if="data.total">
      <el-pagination
        @current-change="load"
        background
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
import { ElMessage } from "element-plus";
import { examDataList, examDataExport } from "@/api/exam.js";

const data = reactive({
  tableData: [],
  pageNum: 1,
  pageSize: 10,
  total: 0,
  userName: "",
  subject: "",
  simulationMode: "",
  subjectOptions: ["英语", "数学", "政治", "专业课"],
});

const formatDuration = (seconds) => {
  if (!seconds) return "-";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}分${s}秒`;
};

const load = () => {
  examDataList({
    pageNum: data.pageNum,
    pageSize: data.pageSize,
    userName: data.userName || undefined,
    subject: data.subject || undefined,
    simulationMode: data.simulationMode || undefined,
  }).then((res) => {
    if (res.code === "200") {
      const page = res.data;
      data.tableData = page.list || [];
      data.total = page.total || 0;
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const reset = () => {
  data.userName = "";
  data.subject = "";
  data.simulationMode = "";
  data.pageNum = 1;
  load();
};

const handleExport = () => {
  examDataExport()
    .then((res) => {
      const blob = new Blob([res.data]);
      const contentDisposition = res.headers?.["content-disposition"] || "";
      let downloadName = "考试数据记录.xlsx";
      const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
      const normalMatch = contentDisposition.match(/filename="?([^"]+)"?/i);
      if (utf8Match?.[1]) {
        downloadName = decodeURIComponent(utf8Match[1]);
      } else if (normalMatch?.[1]) {
        downloadName = normalMatch[1];
      }
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = downloadName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(link.href);
      ElMessage.success("导出成功");
    })
    .catch(() => {
      ElMessage.error("导出失败");
    });
};

load();
</script>
