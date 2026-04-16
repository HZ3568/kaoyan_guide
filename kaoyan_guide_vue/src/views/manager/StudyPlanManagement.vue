<template>
  <div>
    <div class="card" style="margin-bottom: 5px">
      <el-input
        v-model="data.userId"
        style="width: 200px; margin-right: 10px"
        placeholder="用户ID"
        clearable
      />
      <el-button type="info" plain @click="load">查询</el-button>
      <el-button type="warning" plain style="margin: 0 10px" @click="reset">重置</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px">
      <el-table stripe :data="data.tableData">
        <el-table-column prop="userId" label="用户ID" width="80" />
        <el-table-column prop="userName" label="用户名" width="110">
          <template #default="scope">
            {{ scope.row.userName || ('用户' + scope.row.userId) }}
          </template>
        </el-table-column>
        <el-table-column prop="planDate" label="计划日期" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.planStatus)">
              {{ getStatusLabel(scope.row.planStatus) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="任务进度" width="180">
          <template #default="scope">
            <span v-if="scope.row.totalCount === 0" style="color: #909399">无任务</span>
            <template v-else>
              <span style="font-weight: 600">{{ scope.row.completedCount }}</span>
              <span style="color: #999"> / {{ scope.row.totalCount }}</span>
              <el-progress
                :percentage="scope.row.taskPercent || 0"
                :stroke-width="6"
                style="display: inline-block; width: 80px; margin-left: 8px; vertical-align: middle"
              />
            </template>
          </template>
        </el-table-column>
        <el-table-column label="用户反馈" min-width="150">
          <template #default="scope">
            <span
              v-if="scope.row.userFeedback && scope.row.userFeedback !== '暂无反馈'"
              class="clickable-text text-ellipsis"
              @click="showFeedbackDialog(scope.row)"
            >
              {{ scope.row.userFeedbackSummary || scope.row.userFeedback }}
            </span>
            <span v-else style="color: #c0c4cc">暂无反馈</span>
          </template>
        </el-table-column>
        <el-table-column label="AI建议" min-width="150">
          <template #default="scope">
            <span
              v-if="scope.row.aiAdvice && scope.row.aiAdvice !== '暂无建议'"
              class="clickable-text text-ellipsis"
              @click="showAdviceDialog(scope.row)"
            >
              {{ scope.row.aiAdviceSummary || scope.row.aiAdvice }}
            </span>
            <span v-else style="color: #c0c4cc">暂无建议</span>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="170" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="showDetail(scope.row)">查看详情</el-button>
            <el-button type="danger" link @click="handleDeletePlan(scope.row)">删除</el-button>
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

    <!-- 计划详情弹窗 -->
    <el-dialog title="学习计划详情" v-model="data.detailVisible" width="780px" destroy-on-close>
      <div v-if="!data.detail" style="text-align: center; color: #999; padding: 30px">
        加载中...
      </div>
      <div v-else class="detail-wrap">
        <!-- 基本信息区 -->
        <div class="detail-base">
          <div class="detail-base-item">
            <span class="detail-label">用户</span>
            <span class="detail-value">{{ data.detail.userName || ('用户' + data.detail.userId) }}</span>
          </div>
          <div class="detail-base-item">
            <span class="detail-label">计划日期</span>
            <span class="detail-value">{{ data.detail.planDate }}</span>
          </div>
          <div class="detail-base-item">
            <span class="detail-label">状态</span>
            <el-tag :type="getStatusType(data.detail.planStatus)">
              {{ getStatusLabel(data.detail.planStatus) }}
            </el-tag>
          </div>
          <div class="detail-base-item">
            <span class="detail-label">任务进度</span>
            <span v-if="data.detail.totalCount === 0" class="detail-value">无任务</span>
            <span v-else class="detail-value">
              {{ data.detail.completedCount }} / {{ data.detail.totalCount }}
              ({{ data.detail.taskPercent || 0 }}%)
            </span>
          </div>
          <div class="detail-base-item">
            <span class="detail-label">创建时间</span>
            <span class="detail-value">{{ data.detail.createTime || '-' }}</span>
          </div>
          <div class="detail-base-item">
            <span class="detail-label">更新时间</span>
            <span class="detail-value">{{ data.detail.updateTime || '-' }}</span>
          </div>
        </div>

        <!-- 用户反馈 -->
        <div class="detail-section">
          <div class="detail-section-title">
            <el-icon color="#5B50E7"><Connection /></el-icon>
            你的状态反馈
          </div>
          <div class="detail-feedback">
            {{ data.detail.userFeedback || '（无）' }}
          </div>
        </div>

        <!-- AI导师建议 -->
        <div class="detail-section">
          <div class="detail-section-title">
            <el-icon color="#5B50E7"><ChatLineRound /></el-icon>
            AI 导师建议
          </div>
          <div class="detail-advice">
            {{ data.detail.aiAdvice || '（无）' }}
          </div>
        </div>

        <!-- 任务清单 -->
        <div class="detail-section">
          <div class="detail-section-title">
            <el-icon color="#5B50E7"><CircleCheck /></el-icon>
            专属任务清单
          </div>
          <div v-if="!data.detail.tasks || data.detail.tasks.length === 0" class="detail-empty">
            暂无任务
          </div>
          <div v-else class="detail-task-list">
            <div
              v-for="(task, idx) in data.detail.tasks"
              :key="task.taskId || idx"
              class="detail-task-card"
              :class="{ 'is-completed': task.completed }"
            >
              <div class="detail-task-left">
                <div
                  class="detail-checkbox"
                  :class="{ checked: task.completed }"
                >
                  <el-icon v-if="task.completed" color="#fff" :size="12"><Check /></el-icon>
                </div>
                <div class="detail-task-main">
                  <el-tag size="small" :type="getSubjectTagType(task.subject)" effect="light" class="detail-task-tag">
                    {{ task.subject || '未分类' }}
                  </el-tag>
                  <div
                    class="detail-task-content"
                    :class="{ 'text-through': task.completed }"
                  >
                    {{ task.content }}
                  </div>
                </div>
              </div>
              <div class="detail-task-right">
                <el-tag size="small" type="info">{{ task.taskSource === 'DEFERRED' ? '顺延' : '生成' }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="data.detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 用户反馈详情弹窗 -->
    <el-dialog title="用户反馈详情" v-model="data.feedbackDialogVisible" width="560px" destroy-on-close>
      <div v-if="!data.feedbackDialogContent" style="color: #c0c4cc; text-align: center; padding: 20px">
        暂无用户反馈
      </div>
      <div v-else class="dialog-content-box">
        {{ data.feedbackDialogContent }}
      </div>
      <template #footer>
        <el-button @click="data.feedbackDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- AI建议详情弹窗 -->
    <el-dialog title="AI导师建议详情" v-model="data.adviceDialogVisible" width="560px" destroy-on-close>
      <div v-if="!data.adviceDialogContent" style="color: #c0c4cc; text-align: center; padding: 20px">
        暂无AI建议
      </div>
      <div v-else class="dialog-content-box ai-advice-box">
        {{ data.adviceDialogContent }}
      </div>
      <template #footer>
        <el-button @click="data.adviceDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Connection, ChatLineRound, CircleCheck, Check } from "@element-plus/icons-vue";
import {
  studyPlanList,
  studyPlanDetail,
  studyPlanTaskUpdate,
  studyPlanTaskDelete,
  studyPlanDelete,
} from "@/api/ai.js";

const data = reactive({
  tableData: [],
  pageNum: 1,
  pageSize: 10,
  total: 0,
  userId: "",
  detailVisible: false,
  detail: null,
  feedbackDialogVisible: false,
  feedbackDialogContent: "",
  adviceDialogVisible: false,
  adviceDialogContent: "",
});

const getStatusLabel = (status) => {
  if (status === 'GENERATED') return '已完成';
  if (status === 'IN_PROGRESS') return '进行中';
  return '未开始';
};

const getStatusType = (status) => {
  if (status === 'GENERATED') return 'success';
  if (status === 'IN_PROGRESS') return 'warning';
  return 'info';
};

const showFeedbackDialog = (row) => {
  const content = row && row.userFeedback ? row.userFeedback : "";
  data.feedbackDialogContent = content;
  data.feedbackDialogVisible = true;
};

const showAdviceDialog = (row) => {
  const content = row && row.aiAdvice ? row.aiAdvice : "";
  data.adviceDialogContent = content;
  data.adviceDialogVisible = true;
};

const getSubjectTagType = (subject) => {
  if (!subject) return 'info';
  if (subject.includes('数学')) return 'primary';
  if (subject.includes('英语')) return 'warning';
  if (subject.includes('政治')) return 'danger';
  return 'success';
};

const load = () => {
  studyPlanList({
    pageNum: data.pageNum,
    pageSize: data.pageSize,
    userId: data.userId ? Number(data.userId) : undefined,
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
  data.pageNum = 1;
  load();
};

const showDetail = (row) => {
  studyPlanDetail({ planId: row.planId }).then((res) => {
    if (res.code === "200") {
      data.detail = res.data;
      data.detailVisible = true;
    } else {
      ElMessage.error(res.msg || "加载详情失败");
    }
  });
};

const handleDeletePlan = (row) => {
  ElMessageBox.confirm(
    `确认删除 ${row.userName || ('用户' + row.userId)} 于 ${row.planDate} 的学习计划吗？删除后不可恢复。`,
    "删除确认",
    { type: "warning" }
  ).then(() => {
    studyPlanDelete({
      userId: row.userId,
      dateStr: row.planDate,
    }).then((res) => {
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
.text-ellipsis {
  display: inline-block;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: middle;
}

.detail-wrap {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-base {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 20px;
  background: #f8f9fb;
  border-radius: 12px;
}

.detail-base-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-label {
  font-size: 12px;
  color: #909399;
}

.detail-value {
  font-size: 15px;
  color: #303133;
  font-weight: 600;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.detail-feedback {
  padding: 16px;
  background: #f8f9fb;
  border-radius: 10px;
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  font-style: italic;
}

.detail-advice {
  padding: 16px;
  background: #ebf5ff;
  border-radius: 10px;
  font-size: 14px;
  color: #2d5bff;
  line-height: 1.8;
}

.detail-empty {
  text-align: center;
  color: #c0c4cc;
  padding: 24px;
  font-size: 14px;
}

.detail-task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-task-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 14px 16px;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  transition: all 0.2s;
}

.detail-task-card:hover {
  border-color: #5B50E7;
  box-shadow: 0 2px 8px rgba(91, 80, 231, 0.08);
}

.detail-task-card.is-completed {
  background: #f8f9fb;
  border-color: #e4e7ed;
}

.detail-task-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.detail-checkbox {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
  transition: all 0.2s;
}

.detail-checkbox.checked {
  background: #5B50E7;
  border-color: #5B50E7;
}

.detail-task-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-task-tag {
  width: fit-content;
  font-weight: 600;
  border-radius: 4px;
}

.detail-task-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
}

.detail-task-content.text-through {
  text-decoration: line-through;
  color: #c0c4cc;
}

.detail-task-right {
  flex-shrink: 0;
}

.clickable-text {
  color: #5B50E7;
  cursor: pointer;
}
.clickable-text:hover {
  text-decoration: underline;
}

.dialog-content-box {
  padding: 16px 20px;
  background: #f8f9fb;
  border-radius: 10px;
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-all;
}

.ai-advice-box {
  background: #ebf5ff;
  color: #2d5bff;
  border: 1px solid rgba(45, 91, 255, 0.1);
}
</style>
