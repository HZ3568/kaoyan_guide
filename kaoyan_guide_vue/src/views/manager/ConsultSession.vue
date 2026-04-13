<template>
  <div>
    <div class="card" style="margin-bottom: 5px">
      <el-input
        v-model="data.userId"
        style="width: 200px; margin-right: 10px"
        placeholder="用户ID"
        clearable
      />
      <el-select
        v-model="data.moduleType"
        clearable
        placeholder="模块类型"
        style="width: 180px; margin-right: 10px"
      >
        <el-option label="考研院校咨询" value="consult_college" />
        <el-option label="AI学习规划" value="learning_plan" />
      </el-select>
      <el-button type="info" plain @click="load">查询</el-button>
      <el-button type="warning" plain style="margin: 0 10px" @click="reset">重置</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px">
      <el-table stripe :data="data.tableData">
        <el-table-column prop="userId" label="用户ID" width="100" />
        <el-table-column prop="moduleType" label="模块" width="160">
          <template #default="scope">
            {{ moduleTypeLabel(scope.row.moduleType) }}
          </template>
        </el-table-column>
        <el-table-column prop="sessionId" label="会话ID" min-width="200" show-overflow-tooltip />
        <el-table-column prop="messageCount" label="消息数" width="90" />
        <el-table-column prop="lastMessage" label="最后一条消息" min-width="200" show-overflow-tooltip />
        <el-table-column prop="updatedAt" label="最后活跃时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="showHistory(scope.row)">查看详情</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
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

    <!-- 会话详情弹窗 -->
    <el-dialog title="会话历史" v-model="data.historyVisible" width="700px" destroy-on-close>
      <div v-if="data.history.length === 0" style="text-align: center; color: #999; padding: 30px">
        暂无会话记录
      </div>
      <div v-else class="history-list">
        <div
          v-for="(msg, idx) in data.history"
          :key="idx"
          class="history-item"
          :class="msg.type === 'USER' ? 'history-user' : 'history-ai'"
        >
          <div class="history-label">{{ msg.type === 'USER' ? '用户' : 'AI' }}</div>
          <div class="history-content">{{ stripPrefix(msg.content) }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="data.historyVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { sessionList, sessionHistory, sessionDelete } from "@/api/ai.js";

const data = reactive({
  tableData: [],
  pageNum: 1,
  pageSize: 10,
  total: 0,
  userId: "",
  moduleType: "",
  historyVisible: false,
  history: [],
  currentMemoryKey: "",
});

const moduleTypeLabel = (type) => {
  if (type === "consult_college") return "考研院校咨询";
  if (type === "learning_plan") return "AI学习规划";
  return type || "-";
};

const stripPrefix = (content) => {
  // 去掉 AI 消息类型的典型前缀，如 "AI: " 或 "SYSTEM: "
  if (!content) return "";
  return content.replace(/^(AI|USER|SYSTEM):\s*/i, "").trim();
};

const load = () => {
  sessionList({
    pageNum: data.pageNum,
    pageSize: data.pageSize,
    userId: data.userId ? Number(data.userId) : undefined,
    moduleType: data.moduleType || undefined,
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
  data.userId = "";
  data.moduleType = "";
  data.pageNum = 1;
  load();
};

const showHistory = (row) => {
  data.currentMemoryKey = row.memoryKey;
  sessionHistory(row.memoryKey).then((res) => {
    if (res.code === "200") {
      data.history = res.data || [];
      data.historyVisible = true;
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const handleDelete = (row) => {
  ElMessageBox.confirm("删除后将清除该会话所有记录，且不可恢复，确认删除吗？", "删除确认", {
    type: "warning",
  }).then(() => {
    sessionDelete(row.memoryKey).then((res) => {
      if (res.code === "200") {
        ElMessage.success("删除成功");
        load();
      } else {
        ElMessage.error(res.msg);
      }
    });
  }).catch(() => {});
};

load();
</script>

<style scoped>
.history-list {
  max-height: 500px;
  overflow-y: auto;
  padding: 10px;
}
.history-item {
  margin-bottom: 16px;
  padding: 10px 14px;
  border-radius: 8px;
  max-width: 85%;
}
.history-user {
  background: #e8f4ff;
  margin-left: auto;
}
.history-ai {
  background: #f5f5f5;
}
.history-label {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}
.history-content {
  color: #333;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
