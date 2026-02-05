<template>
  <div>
    <div class="card" style="margin-bottom: 5px">
      <el-input
        v-model="data.userName"
        placeholder="请输入学生名称查询"
        style="width: 240px"
      ></el-input>
      <el-button type="info" plain style="margin-left: 10px" @click="load"
        >查询</el-button
      >
      <el-button type="warning" plain style="margin-left: 10px" @click="reset"
        >重置</el-button
      >
    </div>

    <div
      class="card"
      style="margin-bottom: 5px"
      v-if="data.user.role === 'ADMIN'"
    >
      <el-button type="danger" plain @click="delBatch">批量删除</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px">
      <el-table
        :data="data.tableData"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column
          type="selection"
          width="55"
          v-if="data.user.role === 'ADMIN'"
        ></el-table-column>
        <el-table-column prop="userName" label="学生名称"></el-table-column>
        <el-table-column prop="score" label="高考分数"></el-table-column>
        <el-table-column prop="ranking" label="省排名"></el-table-column>
        <el-table-column prop="areasName" label="考试地区"></el-table-column>
        <el-table-column
          prop="firstUniversityName"
          label="第一志愿学校"
          width="120"
        ></el-table-column>
        <el-table-column
          prop="firstSpecialtysName"
          label="第一志愿专业"
          width="120"
        ></el-table-column>
        <el-table-column prop="firstStatus" label="第一志愿状态" width="120">
          <template v-slot="scope">
            <el-tag type="warning" v-if="scope.row.firstStatus === '待录取'"
              >待录取</el-tag
            >
            <el-tag type="success" v-if="scope.row.firstStatus === '已录取'"
              >已录取</el-tag
            >
            <el-tag type="danger" v-if="scope.row.firstStatus === '未录取'"
              >未录取</el-tag
            >
          </template>
        </el-table-column>
        <el-table-column
          prop="secondUniversityName"
          label="第二志愿学校"
          width="120"
        ></el-table-column>
        <el-table-column
          prop="secondSpecialtysName"
          label="第二志愿专业"
          width="120"
        ></el-table-column>
        <el-table-column prop="secondStatus" label="第二志愿状态" width="120">
          <template v-slot="scope">
            <el-tag type="warning" v-if="scope.row.secondStatus === '待录取'"
              >待录取</el-tag
            >
            <el-tag type="success" v-if="scope.row.secondStatus === '已录取'"
              >已录取</el-tag
            >
            <el-tag type="danger" v-if="scope.row.secondStatus === '未录取'"
              >未录取</el-tag
            >
          </template>
        </el-table-column>
        <el-table-column
          prop="thirdUniversityName"
          label="第三志愿学校"
          width="120"
        ></el-table-column>
        <el-table-column
          prop="thirdSpecialtysName"
          label="第三志愿专业"
          width="120"
        ></el-table-column>
        <el-table-column prop="thirdStatus" label="第三志愿状态" width="120">
          <template v-slot="scope">
            <el-tag type="warning" v-if="scope.row.thirdStatus === '待录取'"
              >待录取</el-tag
            >
            <el-tag type="success" v-if="scope.row.thirdStatus === '已录取'"
              >已录取</el-tag
            >
            <el-tag type="danger" v-if="scope.row.thirdStatus === '未录取'"
              >未录取</el-tag
            >
          </template>
        </el-table-column>
        <el-table-column prop="status" label="志愿状态">
          <template v-slot="scope">
            <el-tag type="warning" v-if="scope.row.status === '待录取'"
              >待录取</el-tag
            >
            <el-tag type="success" v-if="scope.row.status === '已录取'"
              >已录取</el-tag
            >
            <el-tag type="danger" v-if="scope.row.status === '未录取'"
              >未录取</el-tag
            >
          </template>
        </el-table-column>
        <el-table-column
          prop="time"
          label="报考时间"
          show-overflow-tooltip
        ></el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="scope">
            <div v-if="data.user.role === 'UNIVERSITY'">
              <el-button
                type="success"
                @click="firstPass(scope.row)"
                v-if="scope.row.firstUniversityId === data.user.id"
                :disabled="scope.row.firstStatus !== '待录取'"
                >通过</el-button
              >
              <el-button
                type="danger"
                @click="firstRefuse(scope.row)"
                v-if="scope.row.firstUniversityId === data.user.id"
                :disabled="scope.row.firstStatus !== '待录取'"
                >拒绝</el-button
              >

              <el-button
                type="success"
                @click="secondPass(scope.row)"
                v-if="scope.row.secondUniversityId === data.user.id"
                :disabled="
                  scope.row.secondStatus !== '待录取' ||
                  scope.row.firstStatus !== '未录取'
                "
                >通过</el-button
              >
              <el-button
                type="danger"
                @click="secondRefuse(scope.row)"
                v-if="scope.row.secondUniversityId === data.user.id"
                :disabled="
                  scope.row.secondStatus !== '待录取' ||
                  scope.row.firstStatus !== '未录取'
                "
                >拒绝</el-button
              >

              <el-button
                type="success"
                @click="thirdPass(scope.row)"
                v-if="scope.row.thirdUniversityId === data.user.id"
                :disabled="
                  scope.row.thirdStatus !== '待录取' ||
                  scope.row.firstStatus !== '未录取' ||
                  scope.row.secondStatus !== '未录取'
                "
                >通过</el-button
              >
              <el-button
                type="danger"
                @click="thirdRefuse(scope.row)"
                v-if="scope.row.thirdUniversityId === data.user.id"
                :disabled="
                  scope.row.thirdStatus !== '待录取' ||
                  scope.row.firstStatus !== '未录取' ||
                  scope.row.secondStatus !== '未录取'
                "
                >拒绝</el-button
              >
            </div>
            <div v-if="data.user.role === 'ADMIN'">
              <el-button
                type="danger"
                circle
                :icon="Delete"
                @click="del(scope.row.id)"
              ></el-button>
            </div>
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
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import request from "@/utils/request";
import { ElMessage, ElMessageBox } from "element-plus";
import { Delete, Edit } from "@element-plus/icons-vue";
const baseUrl = import.meta.env.VITE_BASE_URL;
const formRef = ref();
const data = reactive({
  user: JSON.parse(localStorage.getItem("xm-user") || "{}"),
  tableData: [],
  total: 0,
  pageNum: 1, // 当前的页码
  pageSize: 5, // 每页的个数
  formVisible: false,
  form: {},
  ids: [],
  userName: null,
});
// 加载表格数据
const load = () => {
  request
    .get("/apply/selectPage", {
      params: {
        pageNum: data.pageNum,
        pageSize: data.pageSize,
        userName: data.userName,
      },
    })
    .then((res) => {
      data.tableData = res.data?.list || [];
      data.total = res.data?.total;
    });
};

// 删除
const del = (id) => {
  ElMessageBox.confirm("删除后数据无法恢复，您确定删除吗?", "删除确认", {
    type: "warning",
  })
    .then((res) => {
      request.delete("/apply/delete/" + id).then((res) => {
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

// 批量删除
const handleSelectionChange = (rows) => {
  data.ids = rows.map((v) => v.id);
};

const delBatch = () => {
  if (!data.ids.length) {
    ElMessage.warning("请选择数据");
    return;
  }
  ElMessageBox.confirm("删除后数据无法恢复，您确定删除吗?", "删除确认", {
    type: "warning",
  })
    .then((res) => {
      request.delete("/apply/delete/batch", { data: data.ids }).then((res) => {
        if (res.code === "200") {
          ElMessage.success("操作成功");
          load(); // 刷新表格数据
        } else {
          ElMessage.error(res.msg);
        }
      });
    })
    .catch((err) => console.log(err));
};

const reset = () => {
  data.userName = null;
  load();
};

load();

// 第一志愿录取
const firstPass = (row) => {
  data.form = JSON.parse(JSON.stringify(row));
  data.form.firstStatus = "已录取";
  data.form.status = "已录取";
  request.put("/apply/update", data.form).then((res) => {
    if (res.code === "200") {
      data.formVisible = false;
      ElMessage.success("操作成功");
      load();
    } else {
      ElMessage.error(res.msg);
    }
  });
};
// 第一志愿拒绝
const firstRefuse = (row) => {
  data.form = JSON.parse(JSON.stringify(row));
  data.form.firstStatus = "未录取";
  request.put("/apply/update", data.form).then((res) => {
    if (res.code === "200") {
      data.formVisible = false;
      ElMessage.success("操作成功");
      load();
    } else {
      ElMessage.error(res.msg);
    }
  });
};

// 第一志愿录取
const secondPass = (row) => {
  data.form = JSON.parse(JSON.stringify(row));
  data.form.secondStatus = "已录取";
  data.form.status = "已录取";
  request.put("/apply/update", data.form).then((res) => {
    if (res.code === "200") {
      data.formVisible = false;
      ElMessage.success("操作成功");
      load();
    } else {
      ElMessage.error(res.msg);
    }
  });
};
// 第一志愿拒绝
const secondRefuse = (row) => {
  data.form = JSON.parse(JSON.stringify(row));
  data.form.secondStatus = "未录取";
  request.put("/apply/update", data.form).then((res) => {
    if (res.code === "200") {
      data.formVisible = false;
      ElMessage.success("操作成功");
      load();
    } else {
      ElMessage.error(res.msg);
    }
  });
};

// 第一志愿录取
const thirdPass = (row) => {
  data.form = JSON.parse(JSON.stringify(row));
  data.form.thirdStatus = "已录取";
  data.form.status = "已录取";
  request.put("/apply/update", data.form).then((res) => {
    if (res.code === "200") {
      data.formVisible = false;
      ElMessage.success("操作成功");
      load();
    } else {
      ElMessage.error(res.msg);
    }
  });
};
// 第一志愿拒绝
const thirdRefuse = (row) => {
  data.form = JSON.parse(JSON.stringify(row));
  data.form.thirdStatus = "未录取";
  data.form.status = "未录取";
  request.put("/apply/update", data.form).then((res) => {
    if (res.code === "200") {
      data.formVisible = false;
      ElMessage.success("操作成功");
      load();
    } else {
      ElMessage.error(res.msg);
    }
  });
};
</script>