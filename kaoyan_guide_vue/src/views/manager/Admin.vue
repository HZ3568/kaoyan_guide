<template>
  <div>
    <!-- 工具栏 -->
    <div class="card toolbar-card">
      <el-input
        v-model="data.name"
        style="width: 200px"
        placeholder="请输入姓名或用户名"
        clearable
      />
      <el-button type="primary" @click="load">查询</el-button>
      <el-button @click="reset">重置</el-button>
    </div>

    <!-- 管理员卡片列表 -->
    <div class="card admin-card">
      <div
        v-for="admin in data.tableData"
        :key="admin.id"
        class="admin-item"
      >
        <div class="admin-left">
          <el-avatar :size="48" :src="admin.avatar || defaultAvatar" />
          <div class="admin-info">
            <div class="admin-name-row">
              <span class="admin-name">{{ admin.name || admin.username }}</span>
              <el-tag size="small" type="warning">管理员</el-tag>
              <el-tag
                size="small"
                :type="admin.status === 1 ? 'success' : 'danger'"
              >
                {{ admin.status === 1 ? '正常' : '禁用' }}
              </el-tag>
            </div>
            <div class="admin-detail">
              <span class="detail-item">
                <el-icon><User /></el-icon>
                {{ admin.username }}
              </span>
              <span class="detail-item" v-if="admin.phone">
                <el-icon><Phone /></el-icon>
                {{ admin.phone }}
              </span>
              <span class="detail-item" v-if="admin.email" :title="admin.email">
                <el-icon><Message /></el-icon>
                {{ admin.email.length > 22 ? admin.email.slice(0, 22) + '…' : admin.email }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <el-empty
        v-if="data.tableData.length === 0"
        description="暂无管理员数据"
      />
    </div>

    <!-- 分页 -->
    <div class="card pagination-card" v-if="data.total > 0">
      <el-pagination
        @current-change="load"
        background
        layout="total, prev, pager, next"
        :page-size="data.pageSize"
        :current-page="data.pageNum"
        :total="data.total"
      />
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import { User, Phone, Message } from "@element-plus/icons-vue";
import request from "@/utils/request.js";
import defaultAvatar from "@/assets/imgs/avatar.png";

const data = reactive({
  tableData: [],
  pageNum: 1,
  pageSize: 10,
  total: 0,
  name: null,
});

const load = () => {
  request.get("/admin/selectPage", {
    params: {
      pageNum: data.pageNum,
      pageSize: data.pageSize,
      name: data.name,
    },
  }).then((res) => {
    if (res.code === "200") {
      data.tableData = res.data?.list || [];
      data.total = res.data?.total || 0;
    }
  });
};

const reset = () => {
  data.name = null;
  data.pageNum = 1;
  load();
};

load();
</script>

<style scoped>
.toolbar-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
}

.admin-card {
  padding: 4px 0;
}

.admin-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.admin-item:last-child {
  border-bottom: none;
}

.admin-item:hover {
  background-color: #fafafa;
}

.admin-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.admin-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.admin-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.admin-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.admin-detail {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

.pagination-card {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px;
}
</style>
