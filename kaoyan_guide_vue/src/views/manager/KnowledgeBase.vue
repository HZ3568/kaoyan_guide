<template>
  <div>
    <div class="card" style="margin-bottom: 5px">
      <el-button type="primary" plain @click="openUpload">上传文档</el-button>
      <el-button type="warning" plain style="margin-left: 10px" @click="reindexAll"
        >批量重建索引</el-button
      >
      <el-input
        v-model="data.query.title"
        style="width: 220px; margin-left: 10px"
        placeholder="标题关键字"
      />
      <el-select
        v-model="data.query.status"
        placeholder="状态"
        clearable
        style="width: 140px; margin-left: 10px"
      >
        <el-option label="上传中" value="UPLOADING" />
        <el-option label="处理中" value="PROCESSING" />
        <el-option label="已解析" value="PARSED" />
        <el-option label="已入库" value="INDEXED" />
        <el-option label="失败" value="FAILED" />
      </el-select>
      <el-select
        v-model="data.query.businessType"
        placeholder="业务类型"
        clearable
        style="width: 160px; margin-left: 10px"
      >
        <el-option label="院校" value="school" />
        <el-option label="政策" value="policy" />
        <el-option label="专业" value="major" />
      </el-select>
      <el-button type="info" plain style="margin-left: 10px" @click="load">查询</el-button>
      <el-button type="warning" plain style="margin-left: 10px" @click="reset">重置</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px">
      <el-table stripe :data="data.tableData">
        <el-table-column prop="title" label="文档标题" min-width="160" show-overflow-tooltip />
        <el-table-column prop="fileName" label="原始文件名" min-width="180" show-overflow-tooltip />
        <el-table-column prop="fileType" label="文件类型" width="90" />
        <el-table-column prop="businessType" label="业务类型" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="statusType(scope.row.status)">
              {{ statusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="segmentCount" label="分片数" width="100" />
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="290" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="showDetail(scope.row)">查看详情</el-button>
            <el-button type="warning" link @click="reindexOne(scope.row)">重新建索引</el-button>
            <el-button type="danger" link @click="remove(scope.row)">删除</el-button>
            <el-button type="success" link @click="download(scope.row)">下载原文件</el-button>
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

    <el-dialog title="上传知识库文档" v-model="data.uploadVisible" width="520px" destroy-on-close>
      <el-form ref="uploadFormRef" :model="data.uploadForm" :rules="data.rules" label-width="90px">
        <el-form-item label="文档标题" prop="title">
          <el-input v-model="data.uploadForm.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item label="业务类型" prop="businessType">
          <el-select v-model="data.uploadForm.businessType" placeholder="请选择业务类型" style="width: 100%">
            <el-option label="院校" value="school" />
            <el-option label="政策" value="policy" />
            <el-option label="专业" value="major" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="data.uploadForm.remark" placeholder="可选" />
        </el-form-item>
        <el-form-item label="上传文件" prop="file">
          <el-upload
            :auto-upload="false"
            :show-file-list="true"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div style="font-size: 12px; color: #909399">仅支持 PDF/TXT/MD</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="data.uploadVisible = false">取消</el-button>
          <el-button type="primary" :loading="data.uploading" @click="submitUpload">提交上传</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog title="文档详情" v-model="data.detailVisible" width="620px" destroy-on-close>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="文档标题">{{ data.detail.title || "-" }}</el-descriptions-item>
        <el-descriptions-item label="文件名">{{ data.detail.fileName || "-" }}</el-descriptions-item>
        <el-descriptions-item label="文件地址">{{ data.detail.fileUrl || "-" }}</el-descriptions-item>
        <el-descriptions-item label="文件类型">{{ data.detail.fileType || "-" }}</el-descriptions-item>
        <el-descriptions-item label="业务类型">{{ data.detail.businessType || "-" }}</el-descriptions-item>
        <el-descriptions-item label="当前状态">
          <el-tag :type="statusType(data.detail.status)">
            {{ statusLabel(data.detail.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="分片数量">{{ data.detail.segmentCount ?? 0 }}</el-descriptions-item>
        <el-descriptions-item label="错误原因">{{ data.detail.errorMessage || "-" }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ data.detail.createTime || "-" }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ data.detail.updateTime || "-" }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="data.detailVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  knowledgeBaseDelete,
  knowledgeBaseDetail,
  knowledgeBasePage,
  knowledgeBaseReindex,
  knowledgeBaseReindexAll,
  knowledgeBaseUpload,
} from "@/api/knowledgeBase.js";

const baseUrl = import.meta.env.VITE_BASE_URL;
const uploadFormRef = ref();

const data = reactive({
  tableData: [],
  pageNum: 1,
  pageSize: 10,
  total: 0,
  query: {
    title: "",
    status: "",
    businessType: "",
  },
  uploadVisible: false,
  uploading: false,
  uploadForm: {
    title: "",
    businessType: "school",
    remark: "",
    file: null,
  },
  detailVisible: false,
  detail: {},
  rules: {
    title: [{ required: true, message: "请输入文档标题", trigger: "blur" }],
    businessType: [{ required: true, message: "请选择业务类型", trigger: "change" }],
    file: [{ required: true, message: "请上传文件", trigger: "change" }],
  },
});

const load = () => {
  knowledgeBasePage({
    pageNum: data.pageNum,
    pageSize: data.pageSize,
    title: data.query.title,
    status: data.query.status,
    businessType: data.query.businessType,
  }).then((res) => {
    if (res.code === "200") {
      data.tableData = res.data?.list || [];
      data.total = res.data?.total || 0;
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const reset = () => {
  data.query.title = "";
  data.query.status = "";
  data.query.businessType = "";
  data.pageNum = 1;
  load();
};

const openUpload = () => {
  data.uploadForm = {
    title: "",
    businessType: "school",
    remark: "",
    file: null,
  };
  data.uploadVisible = true;
};

const handleFileChange = (file) => {
  data.uploadForm.file = file.raw;
};

const handleFileRemove = () => {
  data.uploadForm.file = null;
};

const submitUpload = () => {
  uploadFormRef.value.validate((valid) => {
    if (!valid) {
      return;
    }
    const formData = new FormData();
    formData.append("file", data.uploadForm.file);
    formData.append("title", data.uploadForm.title);
    formData.append("businessType", data.uploadForm.businessType || "");
    formData.append("remark", data.uploadForm.remark || "");
    data.uploading = true;
    knowledgeBaseUpload(formData)
      .then((res) => {
        if (res.code === "200") {
          ElMessage.success("上传并入库成功");
          data.uploadVisible = false;
          data.pageNum = 1;
          load();
        } else {
          ElMessage.error(res.msg);
        }
      })
      .finally(() => {
        data.uploading = false;
      });
  });
};

const showDetail = (row) => {
  knowledgeBaseDetail(row.id).then((res) => {
    if (res.code === "200") {
      data.detail = res.data || {};
      data.detailVisible = true;
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const reindexOne = (row) => {
  ElMessageBox.confirm("将重新解析并重建该文档索引，确认继续吗？", "重建确认", { type: "warning" })
    .then(() => {
      knowledgeBaseReindex(row.id).then((res) => {
        if (res.code === "200") {
          ElMessage.success("重建成功");
          load();
        } else {
          ElMessage.error(res.msg);
        }
      });
    })
    .catch(() => {});
};

const reindexAll = () => {
  ElMessageBox.confirm("将按当前筛选范围重建索引，确认继续吗？", "批量重建确认", { type: "warning" })
    .then(() => {
      knowledgeBaseReindexAll({
        businessType: data.query.businessType || "",
        onlySuccess: true,
      }).then((res) => {
        if (res.code === "200") {
          ElMessage.success(`批量重建完成，共处理 ${res.data?.count || 0} 份文档`);
          load();
        } else {
          ElMessage.error(res.msg);
        }
      });
    })
    .catch(() => {});
};

const remove = (row) => {
  ElMessageBox.confirm("删除后将清除文档文件和对应向量，且不可恢复，确认删除吗？", "删除确认", {
    type: "warning",
  })
    .then(() => {
      knowledgeBaseDelete(row.id).then((res) => {
        if (res.code === "200") {
          const result = res.data || {};
          const redisStatus = result.redisDeleted ? "Redis已清理" : "Redis清理失败";
          const dbStatus = result.dbDeleted ? "数据库已删除" : "数据库删除失败";
          const fileStatus = result.localFileDeleted ? "本地文件已删除" : "本地文件删除失败";
          ElMessage.success(`删除成功：${redisStatus}，${dbStatus}，${fileStatus}`);
          load();
        } else {
          ElMessage.error(res.msg);
        }
      });
    })
    .catch(() => {});
};

const download = (row) => {
  window.open(`${baseUrl}/knowledge-base/download/${row.id}?token=${JSON.parse(localStorage.getItem("xm-user") || "{}").token || ""}`);
};

const statusLabel = (status) => {
  if (status === "UPLOADING") return "上传中";
  if (status === "PROCESSING") return "处理中";
  if (status === "PARSED") return "已解析";
  if (status === "INDEXED") return "已入库";
  if (status === "FAILED") return "失败";
  return status || "-";
};

const statusType = (status) => {
  if (status === "UPLOADING") return "info";
  if (status === "PROCESSING") return "primary";
  if (status === "PARSED") return "warning";
  if (status === "INDEXED") return "success";
  if (status === "FAILED") return "danger";
  return "info";
};

load();
</script>
