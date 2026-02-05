<template>
  <div>
    <div class="card" style="margin-bottom: 5px">
      <el-input
        v-model="data.name"
        style="width: 240px; margin-right: 10px"
        placeholder="请输入名称查询"
      ></el-input>
      <el-button type="info" plain @click="load">查询</el-button>
      <el-button type="warning" plain style="margin: 0 10px" @click="reset"
        >重置</el-button
      >
    </div>
    <div class="card" style="margin-bottom: 5px">
      <el-button type="primary" plain @click="handleAdd">新增</el-button>
      <el-button type="danger" plain @click="delBatch">批量删除</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px">
      <el-table
        stripe
        :data="data.tableData"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <!-- <el-table-column prop="username" label="账号" /> -->
        <el-table-column prop="avatar" label="头像">
          <template v-slot="scope">
            <el-image
              style="
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: block;
              "
              v-if="scope.row.avatar"
              :src="scope.row.avatar"
              :preview-src-list="[scope.row.avatar]"
              preview-teleported
            ></el-image>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" show-overflow-tooltip />
        <el-table-column label="所在地" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.address || scope.row.areasName }}
          </template>
        </el-table-column>
        <!-- <el-table-column
          prop="address"
          label="详细地址"
          show-overflow-tooltip
        /> -->
        <el-table-column prop="department" label="主管部门" />
        <el-table-column
          prop="characters"
          label="院校特性"
          show-overflow-tooltip
        />
        <el-table-column
          prop="officialWebsite"
          label="官方网址"
          show-overflow-tooltip
        />
        <el-table-column prop="level" label="办学层次" />
        <!-- <el-table-column prop="role" label="角色" /> -->
        <!-- <el-table-column prop="phone" label="电话" show-overflow-tooltip />
        <el-table-column prop="email" label="邮箱" show-overflow-tooltip /> -->

        <el-table-column prop="content" label="学校简介" width="100">
          <template v-slot="scope">
            <el-button type="primary" @click="preview(scope.row.content)"
              >查看内容</el-button
            >
          </template>
        </el-table-column>
        <!-- <el-table-column prop="status" label="认证状态" width="100">
          <template v-slot="scope">
            <el-tag v-if="scope.row.status === '待认证'" type="warning"
              >待认证</el-tag
            >
            <el-tag v-if="scope.row.status === '待审核'" type="warning"
              >待审核</el-tag
            >
            <el-tag v-if="scope.row.status === '审核通过'" type="success"
              >审核通过</el-tag
            >
            <el-tag v-if="scope.row.status === '审核拒绝'" type="danger"
              >审核拒绝</el-tag
            >
          </template>
        </el-table-column> -->
        <el-table-column label="操作" width="100" fixed="right">
          <template v-slot="scope">
            <el-button
              type="primary"
              circle
              :icon="Edit"
              @click="handleEdit(scope.row)"
            ></el-button>
            <el-button
              type="danger"
              circle
              :icon="Delete"
              @click="del(scope.row.id)"
            ></el-button>
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

    <el-dialog
      title="大学信息"
      v-model="data.formVisible"
      width="40%"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :rules="data.rules"
        :model="data.form"
        label-width="70px"
        style="padding: 20px"
      >
        <el-form-item prop="username" label="账号">
          <el-input
            v-model="data.form.username"
            placeholder="请输入账号"
            :disabled="data.form.id !== undefined"
          ></el-input>
        </el-form-item>
        <el-form-item prop="avatar" label="头像">
          <el-upload
            :action="baseUrl + '/files/upload'"
            :on-success="handleFileUpload"
            list-type="picture"
          >
            <el-button type="primary">点击上传</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item prop="name" label="名称">
          <el-input
            v-model="data.form.name"
            placeholder="请输入名称"
          ></el-input>
        </el-form-item>
        <el-form-item prop="officialWebsite" label="官方网址">
          <el-input
            v-model="data.form.officialWebsite"
            placeholder="请输入官方网址"
          ></el-input>
        </el-form-item>
        <el-form-item prop="address" label="所在地">
          <el-input
            v-model="data.form.address"
            placeholder="请输入所在地"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="data.formVisible = false">取 消</el-button>
          <el-button type="primary" @click="save">确 定</el-button>
        </span>
      </template>
    </el-dialog>
    <el-dialog
      title="内容"
      v-model="data.fromVisibleContent"
      width="50%"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div style="padding: 15px">
        <div v-html="data.content"></div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="data.fromVisibleContent = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import request from "@/utils/request.js";
import { ElMessage, ElMessageBox } from "element-plus";
import { Delete, Edit } from "@element-plus/icons-vue";

const baseUrl = import.meta.env.VITE_BASE_URL;
const formRef = ref();

const data = reactive({
  formVisible: false,
  form: {},
  tableData: [],
  pageNum: 1,
  pageSize: 10,
  total: 0,
  name: null,
  ids: [],
  content: "",
  fromVisibleContent: false,
  rules: {
    username: [{ required: true, message: "请输入账号", trigger: "blur" }],
    name: [{ required: true, message: "请输入名称", trigger: "blur" }],
  },
});

const load = () => {
  request
    .get("/university/selectPage", {
      params: {
        pageNum: data.pageNum,
        pageSize: data.pageSize,
        name: data.name,
      },
    })
    .then((res) => {
      if (res.code === "200") {
        data.tableData = res.data?.list || [];
        data.total = res.data?.total;
      }
    });
};
const handleAdd = () => {
  data.form = {};
  data.formVisible = true;
};
const handleEdit = (row) => {
  data.form = JSON.parse(JSON.stringify(row));
  data.formVisible = true;
};
const add = () => {
  request.post("/university/add", data.form).then((res) => {
    if (res.code === "200") {
      ElMessage.success("操作成功");
      data.formVisible = false;
      load();
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const update = () => {
  request.put("/university/update", data.form).then((res) => {
    if (res.code === "200") {
      ElMessage.success("操作成功");
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

const del = (id) => {
  ElMessageBox.confirm("删除后数据无法恢复，您确定删除吗？", "删除确认", {
    type: "warning",
  })
    .then((res) => {
      request.delete("/university/delete/" + id).then((res) => {
        if (res.code === "200") {
          ElMessage.success("删除成功");
          load();
        } else {
          ElMessage.error(res.msg);
        }
      });
    })
    .catch((err) => {
      console.error(err);
    });
};
const delBatch = () => {
  if (!data.ids.length) {
    ElMessage.warning("请选择数据");
    return;
  }
  ElMessageBox.confirm("删除后数据无法恢复，您确定删除吗？", "删除确认", {
    type: "warning",
  })
    .then((res) => {
      request
        .delete("/university/delete/batch", { data: data.ids })
        .then((res) => {
          if (res.code === "200") {
            ElMessage.success("操作成功");
            load();
          } else {
            ElMessage.error(res.msg);
          }
        });
    })
    .catch((err) => {
      console.error(err);
    });
};
const handleSelectionChange = (rows) => {
  data.ids = rows.map((v) => v.id);
};

const handleFileUpload = (res) => {
  data.form.avatar = res.data;
};

const reset = () => {
  data.name = null;
  load();
};

const preview = (content) => {
  data.content = content;
  data.fromVisibleContent = true;
};

load();
</script>