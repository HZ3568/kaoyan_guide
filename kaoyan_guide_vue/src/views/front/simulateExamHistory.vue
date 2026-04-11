<template>
  <div class="history-page">
    <!-- 顶部切换 -->
    <div class="page-header">
      <div class="view-tabs">
        <span class="view-tab" @click="$router.push('/front/simulateExam')">近五次</span>
        <span class="view-tab active">全部</span>
      </div>
      <el-button type="success" @click="exportXlsx">
        <el-icon><Download /></el-icon> 导出 xlsx
      </el-button>
    </div>

    <!-- 历史记录表格 -->
    <el-table :data="tableData" border stripe style="width: 100%" v-loading="loading">
      <el-table-column prop="subject" label="科目" width="90" align="center" />
      <el-table-column label="试题出处" min-width="160">
        <template #default="{ row }">
          {{ row.questionSource && row.questionSource.trim() ? row.questionSource : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="score" label="成绩" width="80" align="center" />
      <el-table-column label="用时" width="110" align="center">
        <template #default="{ row }">{{ formatDuration(row.durationSeconds) }}</template>
      </el-table-column>
      <el-table-column label="模拟模式" width="110" align="center">
        <template #default="{ row }">
          {{ row.simulationMode || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="提交时间" width="170" align="center">
        <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="90" align="center" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" link @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrap">
      <el-pagination
        :current-page="pageNum"
        :page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="(val) => { pageSize = val; pageNum = 1; loadData(); }"
        @current-change="(val) => { pageNum = val; loadData(); }"
      />
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog title="编辑记录" v-model="editVisible" width="440px" :close-on-click-modal="false">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="考试科目">
          <el-select v-model="editForm.subject" style="width: 100%">
            <el-option label="政治" value="政治" />
            <el-option label="英语" value="英语" />
            <el-option label="数学" value="数学" />
            <el-option label="专业课" value="专业课" />
          </el-select>
        </el-form-item>
        <el-form-item label="试题出处">
          <el-input v-model="editForm.questionSource" placeholder="试题出处" />
        </el-form-item>
        <el-form-item label="考试成绩">
          <el-input v-model.number="editForm.score" type="number" min="0" max="150" />
        </el-form-item>
        <el-form-item label="用时(秒)">
          <el-input v-model.number="editForm.durationSeconds" type="number" min="0" />
        </el-form-item>
        <el-form-item label="模拟模式">
          <el-select v-model="editForm.simulationMode" style="width: 100%">
            <el-option label="演示模式" value="演示模式" />
            <el-option label="标准模式" value="标准模式" />
          </el-select>
        </el-form-item>
        <el-form-item label="提交时间">
          <el-date-picker
            v-model="editForm.createTime"
            type="datetime"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Download } from "@element-plus/icons-vue";
import request from "@/utils/request";

const loading = ref(false);
const tableData = ref([]);
const total = ref(0);
const pageNum = ref(1);
const pageSize = ref(10);

const editVisible = ref(false);
const editForm = ref({});

const loadData = () => {
  loading.value = true;
  request
    .get("/exam/history", { params: { pageNum: pageNum.value, pageSize: pageSize.value } })
    .then((res) => {
      if (res.code === "200") {
        tableData.value = res.data || [];
        total.value = res.total || 0;
      }
    })
    .finally(() => {
      loading.value = false;
    });
};

const formatDuration = (seconds) => {
  if (!seconds && seconds !== 0) return "-";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
};

const formatTime = (t) => {
  if (!t) return "-";
  return t.replace("T", " ").slice(0, 19);
};

const openEdit = (row) => {
  // createTime 可能是 "2024-01-01T12:00:00" 或 "2024-01-01 12:00:00"
  const ct = row.createTime ? row.createTime.replace(" ", "T").slice(0, 19) : null;
  editForm.value = { ...row, createTime: ct };
  editVisible.value = true;
};

const submitEdit = () => {
  request.put("/exam/update", editForm.value).then((res) => {
    if (res.code === "200") {
      ElMessage.success("更新成功");
      editVisible.value = false;
      loadData();
    } else {
      ElMessage.error(res.msg || "更新失败");
    }
  });
};

const exportXlsx = () => {
  request
    .get("/exam/export", { responseType: "blob" })
    .then((blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "考场模拟历史记录.xlsx";
      a.click();
      URL.revokeObjectURL(url);
    })
    .catch(() => {
      ElMessage.error("导出失败，请稍后重试");
    });
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.history-page {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: #f5f7fa;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.view-tabs {
  display: flex;
  gap: 4px;
  background: #fff;
  border-radius: 20px;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.view-tab {
  padding: 6px 18px;
  border-radius: 16px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  transition: all 0.2s;
  white-space: nowrap;
}
.view-tab.active {
  background: #67c23a;
  color: white;
  box-shadow: 0 2px 6px rgba(103, 194, 58, 0.3);
}
.view-tab:not(.active):hover {
  background: rgba(103, 194, 58, 0.12);
  color: #67c23a;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
