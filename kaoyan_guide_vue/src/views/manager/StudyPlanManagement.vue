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
        <el-table-column prop="userId" label="用户ID" width="100" />
        <el-table-column prop="userName" label="用户名" width="120" />
        <el-table-column prop="planDate" label="计划日期" width="120" />
        <el-table-column label="状态" width="110">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.planStatus)">
              {{ getStatusLabel(scope.row.planStatus) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="任务进度" width="160">
          <template #default="scope">
            <span v-if="taskProgress(scope.row) === 0" style="color: #909399">未开始</span>
            <span v-else-if="taskProgress(scope.row) === 100" style="color: #67c23a; font-weight: 600">已完成</span>
            <template v-else>
              <span>{{ scope.row.completedCount || 0 }} / {{ scope.row.totalCount || 0 }}</span>
              <el-progress
                :percentage="taskProgress(scope.row)"
                :stroke-width="6"
                style="display: inline-block; width: 70px; margin-left: 6px; vertical-align: middle"
              />
            </template>
          </template>
        </el-table-column>
        <el-table-column label="用户反馈" min-width="140">
          <template #default="scope">
            {{ scope.row.userFeedback || '暂无反馈' }}
          </template>
        </el-table-column>
        <el-table-column label="AI建议" min-width="160">
          <template #default="scope">
            {{ scope.row.aiAdvice || '暂无建议' }}
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="showTasks(scope.row)">查看任务</el-button>
            <el-button type="danger" link @click="handleDeletePlan(scope.row)">删除计划</el-button>
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

    <!-- 任务详情弹窗 -->
    <el-dialog title="学习任务详情" v-model="data.taskVisible" width="800px" destroy-on-close>
      <div v-if="data.currentTasks.length === 0" style="text-align: center; color: #999; padding: 30px">
        暂无任务
      </div>
      <el-table v-else stripe :data="data.currentTasks" style="margin-bottom: 10px">
        <el-table-column prop="subject" label="科目" width="100" />
        <el-table-column prop="content" label="任务内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="taskSource" label="来源" width="100" />
        <el-table-column label="完成状态" width="120">
          <template #default="scope">
            <el-checkbox
              :model-value="scope.row.completed"
              @change="toggleTask(scope.row)"
              :label="scope.row.completed ? '已完成' : '未完成'"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="danger" link size="small" @click="deleteTask(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="data.taskVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  studyPlanList,
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
  taskVisible: false,
  currentTasks: [],
  currentPlanId: null,
});

const taskProgress = (row) => {
  const total = row.totalCount || 0;
  if (total === 0) return 0;
  const completed = row.completedCount || 0;
  return Math.round((completed / total) * 100);
};

const getStatusLabel = (status) => {
  if (status === 'GENERATED') return '已完成';
  if (status === 'PENDING') return '进行中';
  return '未开始';
};

const getStatusType = (status) => {
  if (status === 'GENERATED') return 'success';
  if (status === 'PENDING') return 'primary';
  return 'info';
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

const showTasks = (row) => {
  data.currentTasks = row.tasks || [];
  data.currentPlanId = row.id;
  data.taskVisible = true;
};

const toggleTask = (task) => {
  const newCompleted = !task.completed;
  studyPlanTaskUpdate({
    planId: data.currentPlanId,
    taskId: task.taskId,
    completed: newCompleted,
  }).then((res) => {
    if (res.code === "200") {
      ElMessage.success(newCompleted ? "已标记完成" : "已取消完成");
      task.completed = newCompleted;
      load();
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const deleteTask = (task) => {
  ElMessageBox.confirm("确认删除该任务吗？", "删除确认", { type: "warning" }).then(() => {
    studyPlanTaskDelete({
      planId: data.currentPlanId,
      taskId: task.taskId,
    }).then((res) => {
      if (res.code === "200") {
        ElMessage.success("删除成功");
        data.currentTasks = data.currentTasks.filter((t) => t.taskId !== task.taskId);
        load();
      } else {
        ElMessage.error(res.msg);
      }
    });
  }).catch(() => {});
};

const handleDeletePlan = (row) => {
  ElMessageBox.confirm(
    `确认删除用户 ${row.userId} 于 ${row.planDate} 的学习计划吗？删除后不可恢复。`,
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
