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
      <el-button type="success" @click="handleAdd">
        <el-icon><Plus /></el-icon> 新增用户
      </el-button>
    </div>

    <!-- 用户卡片列表 -->
    <div class="card user-card" v-loading="data.loading">
      <div
        v-for="user in data.tableData"
        :key="user.id"
        class="user-item"
      >
        <!-- 左侧：头像 + 基本信息 -->
        <div class="user-left">
          <el-avatar :size="48" :src="user.avatar || defaultAvatar" />
          <div class="user-info">
            <div class="user-name-row">
              <span class="user-name">{{ user.name || user.username }}</span>
              <el-tag size="small" type="success">学生</el-tag>
              <el-tag
                size="small"
                :type="user.status === 1 ? 'success' : 'danger'"
                class="status-tag"
              >
                {{ user.status === 1 ? '正常' : '禁用' }}
              </el-tag>
            </div>
            <div class="user-detail">
              <span class="detail-item">
                <el-icon><User /></el-icon>
                {{ user.username }}
              </span>
              <span class="detail-item" v-if="user.phone">
                <el-icon><Phone /></el-icon>
                {{ user.phone }}
              </span>
              <span class="detail-item" v-if="user.email" :title="user.email">
                <el-icon><Message /></el-icon>
                {{ user.email.length > 20 ? user.email.slice(0, 20) + '…' : user.email }}
              </span>
            </div>
          </div>
        </div>

        <!-- 右侧：操作按钮 -->
        <div class="user-actions">
          <el-switch
            v-model="user.status"
            :active-value="1"
            :inactive-value="0"
            active-text="正常"
            inactive-text="禁用"
            inline-prompt
            @change="handleStatusChange(user)"
          />
          <el-button type="primary" plain size="small" @click="handleEdit(user)">
            编辑
          </el-button>
          <el-button type="danger" plain size="small" @click="handleDelete(user.id)">
            删除
          </el-button>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="!data.loading && data.tableData.length === 0"
        description="暂无用户数据"
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

    <!-- 编辑/新增弹窗 -->
    <el-dialog
      :title="data.form.id ? '编辑用户' : '新增用户'"
      v-model="data.formVisible"
      width="500px"
      destroy-on-close
    >
      <el-form ref="formRef" :rules="data.rules" :model="data.form" label-width="70px">
        <el-form-item prop="username" label="账号">
          <el-input
            v-model="data.form.username"
            placeholder="请输入账号（3-20位）"
            :disabled="!!data.form.id"
          />
        </el-form-item>
        <el-form-item prop="name" label="姓名">
          <el-input v-model="data.form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item prop="phone" label="电话">
          <el-input
            v-model="data.form.phone"
            placeholder="请输入11位数字电话"
            maxlength="11"
          />
        </el-form-item>
        <el-form-item prop="email" label="邮箱">
          <el-input v-model="data.form.email" placeholder="请输入标准格式邮箱" />
        </el-form-item>
        <el-form-item prop="status" label="状态">
          <el-radio-group v-model="data.form.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="data.formVisible = false">取消</el-button>
        <el-button type="primary" @click="save">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, User, Phone, Message } from "@element-plus/icons-vue";
import defaultAvatar from "@/assets/imgs/avatar.png";
import request from "@/utils/request.js";

const formRef = ref();

const validatePhone = (rule, value, callback) => {
  if (value && !/^\d{11}$/.test(value)) {
    callback(new Error("电话必须为11位数字"));
  } else {
    callback();
  }
};

const validateEmail = (rule, value, callback) => {
  if (value && !/^[\w.-]+@[\w.-]+\.\w+$/.test(value)) {
    callback(new Error("邮箱格式不正确"));
  } else {
    callback();
  }
};

const data = reactive({
  loading: false,
  formVisible: false,
  form: {},
  tableData: [],
  pageNum: 1,
  pageSize: 10,
  total: 0,
  name: null,
  rules: {
    username: [
      { required: true, message: "请输入账号", trigger: "blur" },
      { min: 3, max: 20, message: "账号长度为3-20位", trigger: "blur" },
    ],
    phone: [{ validator: validatePhone, trigger: "blur" }],
    email: [{ validator: validateEmail, trigger: "blur" }],
  },
});

const load = () => {
  data.loading = true;
  request
    .get("/user/selectPage", {
      params: {
        pageNum: data.pageNum,
        pageSize: data.pageSize,
        name: data.name,
      },
    })
    .then((res) => {
      if (res.code === "200") {
        data.tableData = res.data?.list || [];
        data.total = res.data?.total || 0;
      }
    })
    .finally(() => {
      data.loading = false;
    });
};

const handleStatusChange = (user) => {
  request.put("/user/update", user).then((res) => {
    if (res.code === "200") {
      ElMessage.success("状态更新成功");
    } else {
      ElMessage.error(res.msg || "操作失败");
      load();
    }
  });
};

const handleAdd = () => {
  data.form = { status: 1 };
  data.formVisible = true;
};

const handleEdit = (row) => {
  data.form = JSON.parse(JSON.stringify(row));
  data.formVisible = true;
};

const add = () => {
  request.post("/user/add", data.form).then((res) => {
    if (res.code === "200") {
      ElMessage.success("新增成功");
      data.formVisible = false;
      load();
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const update = () => {
  request.put("/user/update", data.form).then((res) => {
    if (res.code === "200") {
      ElMessage.success("更新成功");
      data.formVisible = false;
      load();
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const save = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      data.form.id ? update() : add();
    }
  });
};

const handleDelete = (id) => {
  ElMessageBox.confirm("删除后不可恢复，确定要删除吗？", "删除确认", {
    confirmButtonText: "删除",
    cancelButtonText: "取消",
    type: "warning",
  }).then(() => {
    request.delete("/user/delete/" + id).then((res) => {
      if (res.code === "200") {
        ElMessage.success("删除成功");
        load();
      } else {
        ElMessage.error(res.msg);
      }
    });
  }).catch(() => {});
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

.user-card {
  padding: 4px 0;
}

.user-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.user-item:last-child {
  border-bottom: none;
}

.user-item:hover {
  background-color: #fafafa;
}

.user-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.user-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.user-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.status-tag {
  font-size: 12px;
}

.user-detail {
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

.user-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.pagination-card {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px;
}
</style>
