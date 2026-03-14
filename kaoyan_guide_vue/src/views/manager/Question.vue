<template>
  <div>
    <div class="card" style="margin-bottom: 5px">
      <el-input v-model="data.title" style="width: 220px; margin-right: 10px" placeholder="请输入题干关键词"></el-input>
      <el-select v-model="data.subject" clearable placeholder="科目" style="width: 120px; margin-right: 10px">
        <el-option v-for="item in data.subjectOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-select v-model="data.type" clearable placeholder="题型" style="width: 140px; margin-right: 10px">
        <el-option v-for="item in data.typeOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-select v-model="data.difficulty" clearable placeholder="难度" style="width: 110px; margin-right: 10px">
        <el-option v-for="item in data.difficultyOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-select v-model="data.status" clearable placeholder="状态" style="width: 110px; margin-right: 10px">
        <el-option label="启用" :value="1" />
        <el-option label="禁用" :value="0" />
      </el-select>
      <el-button type="info" plain @click="load">查询</el-button>
      <el-button type="warning" plain style="margin: 0 10px" @click="reset">重置</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px">
      <el-button type="primary" plain @click="handleAdd">新增题目</el-button>
      <el-button type="danger" plain @click="delBatch">批量删除</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px">
      <el-table stripe :data="data.tableData" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="题目ID" width="90" />
        <el-table-column prop="subject" label="科目" width="100" />
        <el-table-column prop="type" label="题型" width="130">
          <template #default="scope">
            {{ getTypeLabel(scope.row.type) }}
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="90" />
        <el-table-column prop="title" label="题干" show-overflow-tooltip min-width="220" />
        <el-table-column prop="correctAnswer" label="正确答案" width="120" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-switch :model-value="scope.row.status === 1" @change="toggleStatus(scope.row)" />
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="scope">
            <el-button type="primary" circle :icon="Edit" @click="handleEdit(scope.row)"></el-button>
            <el-button type="danger" circle :icon="Delete" @click="del(scope.row.id)"></el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="card" v-if="data.total" style="margin-bottom: 5px">
      <el-pagination @current-change="load" background layout="total, prev, pager, next" :page-size="data.pageSize" v-model:current-page="data.pageNum" :total="data.total" />
    </div>

    <div class="card" style="margin-bottom: 5px">
      <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap">
        <div style="font-weight: 600">指定今日题目</div>
        <el-date-picker v-model="data.assignDate" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 150px" />
        <el-select v-model="data.assignQuestionId" filterable clearable placeholder="选择题目" style="width: 260px">
          <el-option v-for="item in data.enabledQuestionList" :key="'q' + item.id" :value="item.id" :label="'#' + item.id + ' ' + item.title" />
        </el-select>
        <el-button type="primary" @click="assignDaily">保存指定</el-button>
        <el-button plain @click="loadAssignments">刷新记录</el-button>
      </div>
      <div style="margin-top: 12px">
        <el-table :data="data.assignmentList" stripe>
          <el-table-column prop="questionDate" label="日期" width="120" />
          <el-table-column prop="questionId" label="题目ID" width="90" />
          <el-table-column prop="subject" label="科目" width="100" />
          <el-table-column prop="type" label="题型" width="130">
            <template #default="scope">
              {{ getTypeLabel(scope.row.type) }}
            </template>
          </el-table-column>
          <el-table-column prop="difficulty" label="难度" width="90" />
          <el-table-column prop="title" label="题干" show-overflow-tooltip />
        </el-table>
      </div>
    </div>

    <el-dialog :title="data.form.id ? '编辑题目' : '新增题目'" v-model="data.formVisible" width="52%" destroy-on-close>
      <el-form ref="formRef" :rules="data.rules" :model="data.form" label-width="92px" style="padding: 18px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="科目" prop="subject">
              <el-select v-model="data.form.subject" placeholder="请选择科目">
                <el-option v-for="item in data.subjectOptions" :key="'s' + item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="题型" prop="type">
              <el-select v-model="data.form.type" placeholder="请选择题型">
                <el-option v-for="item in data.typeOptions" :key="'t' + item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="难度" prop="difficulty">
              <el-select v-model="data.form.difficulty" placeholder="请选择难度">
                <el-option v-for="item in data.difficultyOptions" :key="'d' + item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="题目内容" prop="title">
          <el-input v-model="data.form.title" type="textarea" :rows="4" placeholder="请输入题目内容"></el-input>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="选项A">
              <el-input v-model="data.form.optionA" placeholder="请输入选项A"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="选项B">
              <el-input v-model="data.form.optionB" placeholder="请输入选项B"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="选项C">
              <el-input v-model="data.form.optionC" placeholder="请输入选项C"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="选项D">
              <el-input v-model="data.form.optionD" placeholder="请输入选项D"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="正确答案" prop="correctAnswer">
              <el-input v-model="data.form.correctAnswer" placeholder="请输入正确答案"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-switch v-model="data.form.status" :active-value="1" :inactive-value="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="题目解析">
          <el-input v-model="data.form.analysis" type="textarea" :rows="4" placeholder="请输入题目解析"></el-input>
        </el-form-item>
        <el-form-item label="录入提示">
          <el-alert title="支持 LaTeX：行内可用 \\( ... \\) 或 $ ... $，块级可用 \\[ ... \\] 或 $$ ... $$" type="info" :closable="false" />
        </el-form-item>
        <el-form-item label="预览效果">
          <div class="math-preview">
            <div class="math-preview-item">
              <div class="math-preview-label">题目内容</div>
              <MathContent :content="data.form.title || '-'" />
            </div>
            <div class="math-preview-item" v-if="data.form.optionA || data.form.optionB || data.form.optionC || data.form.optionD">
              <div class="math-preview-label">选项预览</div>
              <div class="math-option-row" v-if="data.form.optionA">
                <span class="math-option-prefix">A.</span>
                <MathContent :content="data.form.optionA" />
              </div>
              <div class="math-option-row" v-if="data.form.optionB">
                <span class="math-option-prefix">B.</span>
                <MathContent :content="data.form.optionB" />
              </div>
              <div class="math-option-row" v-if="data.form.optionC">
                <span class="math-option-prefix">C.</span>
                <MathContent :content="data.form.optionC" />
              </div>
              <div class="math-option-row" v-if="data.form.optionD">
                <span class="math-option-prefix">D.</span>
                <MathContent :content="data.form.optionD" />
              </div>
            </div>
            <div class="math-preview-item">
              <div class="math-preview-label">正确答案</div>
              <MathContent :content="data.form.correctAnswer || '-'" />
            </div>
            <div class="math-preview-item">
              <div class="math-preview-label">题目解析</div>
              <MathContent :content="data.form.analysis || '暂无解析'" />
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span>
          <el-button @click="data.formVisible = false">取消</el-button>
          <el-button type="primary" @click="save">保存</el-button>
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
import MathContent from "@/components/MathContent.vue";

const formRef = ref();
const data = reactive({
  tableData: [],
  total: 0,
  pageNum: 1,
  pageSize: 10,
  title: null,
  subject: null,
  type: null,
  difficulty: null,
  status: null,
  ids: [],
  formVisible: false,
  form: {},
  assignDate: "",
  assignQuestionId: null,
  assignmentList: [],
  enabledQuestionList: [],
  subjectOptions: [
    { label: "英语", value: "英语" },
    { label: "数学", value: "数学" },
    { label: "政治", value: "政治" },
    { label: "专业课", value: "专业课" },
  ],
  typeOptions: [
    { label: "单选题", value: "single_choice" },
    { label: "判断题", value: "judge" },
    { label: "简答题", value: "short_answer" },
  ],
  difficultyOptions: [
    { label: "easy", value: "easy" },
    { label: "medium", value: "medium" },
    { label: "hard", value: "hard" },
  ],
  rules: {
    subject: [{ required: true, message: "请选择科目", trigger: "change" }],
    type: [{ required: true, message: "请选择题型", trigger: "change" }],
    difficulty: [{ required: true, message: "请选择难度", trigger: "change" }],
    title: [{ required: true, message: "请输入题目内容", trigger: "blur" }],
    correctAnswer: [{ required: true, message: "请输入正确答案", trigger: "blur" }],
  },
});

const getTypeLabel = (type) => {
  const matched = data.typeOptions.find((item) => item.value === type);
  return matched ? matched.label : type;
};

const load = () => {
  request.get("/question/selectPage", {
    params: {
      pageNum: data.pageNum,
      pageSize: data.pageSize,
      title: data.title,
      subject: data.subject,
      type: data.type,
      difficulty: data.difficulty,
      status: data.status,
    },
  }).then((res) => {
    if (res.code === "200") {
      data.tableData = res.data?.list || [];
      data.total = res.data?.total;
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const loadEnabledQuestions = () => {
  request.get("/question/selectAll", { params: { status: 1 } }).then((res) => {
    if (res.code === "200") {
      data.enabledQuestionList = res.data || [];
    }
  });
};

const loadAssignments = () => {
  request.get("/question/dailyAssignments").then((res) => {
    if (res.code === "200") {
      data.assignmentList = res.data?.list || [];
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const handleAdd = () => {
  data.form = {
    subject: "英语",
    type: "single_choice",
    difficulty: "medium",
    status: 1,
  };
  data.formVisible = true;
};

const handleEdit = (row) => {
  data.form = JSON.parse(JSON.stringify(row));
  data.formVisible = true;
};

const add = () => {
  request.post("/question/add", data.form).then((res) => {
    if (res.code === "200") {
      ElMessage.success("操作成功");
      data.formVisible = false;
      load();
      loadEnabledQuestions();
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const update = () => {
  request.put("/question/update", data.form).then((res) => {
    if (res.code === "200") {
      ElMessage.success("操作成功");
      data.formVisible = false;
      load();
      loadEnabledQuestions();
      loadAssignments();
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

const toggleStatus = (row) => {
  request.put("/question/update", { id: row.id, status: row.status === 1 ? 0 : 1 }).then((res) => {
    if (res.code === "200") {
      ElMessage.success("状态已更新");
      load();
      loadEnabledQuestions();
      loadAssignments();
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const del = (id) => {
  ElMessageBox.confirm("删除后数据无法恢复，您确定删除吗？", "删除确认", { type: "warning" }).then(() => {
    request.delete("/question/delete/" + id).then((res) => {
      if (res.code === "200") {
        ElMessage.success("删除成功");
        load();
        loadEnabledQuestions();
        loadAssignments();
      } else {
        ElMessage.error(res.msg);
      }
    });
  }).catch((err) => {
    console.error(err);
  });
};

const handleSelectionChange = (rows) => {
  data.ids = rows.map((v) => v.id);
};

const delBatch = () => {
  if (!data.ids.length) {
    ElMessage.warning("请选择数据");
    return;
  }
  ElMessageBox.confirm("删除后数据无法恢复，您确定删除吗？", "删除确认", { type: "warning" }).then(() => {
    request.delete("/question/delete/batch", { data: data.ids }).then((res) => {
      if (res.code === "200") {
        ElMessage.success("操作成功");
        load();
        loadEnabledQuestions();
        loadAssignments();
      } else {
        ElMessage.error(res.msg);
      }
    });
  }).catch((err) => {
    console.error(err);
  });
};

const assignDaily = () => {
  if (!data.assignDate) {
    ElMessage.warning("请选择日期");
    return;
  }
  if (!data.assignQuestionId) {
    ElMessage.warning("请选择题目");
    return;
  }
  request.post("/question/assignDaily", {
    questionDate: data.assignDate,
    questionId: String(data.assignQuestionId),
  }).then((res) => {
    if (res.code === "200") {
      ElMessage.success("指定成功");
      loadAssignments();
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const reset = () => {
  data.title = null;
  data.subject = null;
  data.type = null;
  data.difficulty = null;
  data.status = null;
  load();
};

load();
loadEnabledQuestions();
loadAssignments();
</script>

<style scoped>
.math-preview {
  width: 100%;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  background: #fafafa;
}

.math-preview-item + .math-preview-item {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #e4e7ed;
}

.math-preview-label {
  color: #606266;
  font-size: 13px;
  margin-bottom: 6px;
  font-weight: 600;
}

.math-option-row {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin-top: 4px;
}

.math-option-prefix {
  font-weight: 600;
  color: #303133;
  flex-shrink: 0;
}
</style>
