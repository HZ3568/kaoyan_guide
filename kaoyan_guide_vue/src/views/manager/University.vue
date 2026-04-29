<template>
  <div>
    <div class="card" style="margin-bottom: 5px">
      <el-input
        v-model="data.name"
        style="width: 180px; margin-right: 10px"
        placeholder="学校名称"
      ></el-input>
      <el-select
        v-model="data.provinceId"
        placeholder="省份"
        clearable
        style="width: 130px; margin-right: 10px"
        filterable
      >
        <el-option
          v-for="item in data.areasData"
          :key="'p' + item.id"
          :label="item.name"
          :value="item.id"
        />
      </el-select>
      <el-select
        v-model="data.schoolType"
        placeholder="院校类型"
        clearable
        style="width: 130px; margin-right: 10px"
      >
        <el-option
          v-for="item in data.schoolTypeOptions"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
      <el-select
        v-model="data.educationLevel"
        placeholder="办学层次"
        clearable
        style="width: 120px; margin-right: 10px"
      >
        <el-option
          v-for="item in data.educationLevelOptions"
          :key="'qe' + item"
          :label="item"
          :value="item"
        />
      </el-select>
      <el-select
        v-model="data.is985"
        placeholder="985"
        clearable
        style="width: 90px; margin-right: 10px"
      >
        <el-option label="是" :value="1" />
        <el-option label="否" :value="0" />
      </el-select>
      <el-select
        v-model="data.is211"
        placeholder="211"
        clearable
        style="width: 90px; margin-right: 10px"
      >
        <el-option label="是" :value="1" />
        <el-option label="否" :value="0" />
      </el-select>
      <el-select
        v-model="data.isDoubleFirstClass"
        placeholder="双一流"
        clearable
        style="width: 100px; margin-right: 10px"
      >
        <el-option label="是" :value="1" />
        <el-option label="否" :value="0" />
      </el-select>
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
            >
              <template #error>
                <img
                  :src="defaultAvatar"
                  style="
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: block;
                  "
                  alt=""
                />
              </template>
            </el-image>
          </template>
        </el-table-column>
        <el-table-column
          prop="name"
          label="学校名称"
          min-width="160"
          show-overflow-tooltip
        />
        <el-table-column label="所在地" min-width="160" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.provinceName || "-" }}
          </template>
        </el-table-column>
        <el-table-column
          prop="address"
          label="详细地址"
          min-width="180"
          show-overflow-tooltip
        />
        <el-table-column prop="schoolType" label="院校类型" width="110" />
        <el-table-column prop="educationLevel" label="办学层次" width="100" />
        <el-table-column label="标签" width="180">
          <template #default="scope">
            <el-tag size="small" type="danger" v-if="scope.row.is985"
              >985</el-tag
            >
            <el-tag
              size="small"
              type="warning"
              v-if="scope.row.is211"
              style="margin-left: 4px"
              >211</el-tag
            >
            <el-tag
              size="small"
              type="success"
              v-if="scope.row.isDoubleFirstClass"
              style="margin-left: 4px"
              >双一流</el-tag
            >
          </template>
        </el-table-column>
        <el-table-column label="官网" min-width="180" show-overflow-tooltip>
          <template #default="scope">
            <a
              v-if="scope.row.officialWebsite"
              :href="scope.row.officialWebsite"
              target="_blank"
              >{{ scope.row.officialWebsite }}</a
            >
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="170" />
        <el-table-column prop="updateTime" label="更新时间" width="170" />
        <el-table-column prop="description" label="院校简介" width="100">
          <template v-slot="scope">
            <el-button type="primary" @click="preview(scope.row.description)"
              >查看内容</el-button
            >
          </template>
        </el-table-column>
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
      title="院校信息"
      v-model="data.formVisible"
      width="60%"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :rules="data.rules"
        :model="data.form"
        label-width="100px"
        style="padding: 20px"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item prop="name" label="学校名称">
              <el-input
                v-model="data.form.name"
                placeholder="请输入学校名称"
              ></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12"></el-col>
        </el-row>
        <el-form-item prop="avatar" label="头像">
          <el-upload
            :action="baseUrl + '/files/upload'"
            :on-success="handleFileUpload"
            list-type="picture"
          >
            <el-button type="primary">点击上传</el-button>
          </el-upload>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item prop="provinceId" label="省份">
              <el-select
                v-model="data.form.provinceId"
                placeholder="请选择省份"
                clearable
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="item in data.areasData"
                  :key="'fp' + item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12"></el-col>
        </el-row>
        <el-form-item prop="address" label="详细地址">
          <el-input
            v-model="data.form.address"
            placeholder="请输入详细地址"
          ></el-input>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item prop="longitude" label="百度经度">
              <el-input
                v-model="data.form.longitude"
                placeholder="如：116.404269（可选）"
              ></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="latitude" label="百度纬度">
              <el-input
                v-model="data.form.latitude"
                placeholder="如：39.914980（可选）"
              ></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item prop="schoolType" label="院校类型">
              <el-select
                v-model="data.form.schoolType"
                placeholder="请选择院校类型"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="item in data.schoolTypeOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item prop="educationLevel" label="办学层次">
              <el-select
                v-model="data.form.educationLevel"
                placeholder="请选择办学层次"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="item in data.educationLevelOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8"></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item prop="is985" label="985">
              <el-switch
                v-model="data.form.is985"
                :active-value="1"
                :inactive-value="0"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item prop="is211" label="211">
              <el-switch
                v-model="data.form.is211"
                :active-value="1"
                :inactive-value="0"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item prop="isDoubleFirstClass" label="双一流">
              <el-switch
                v-model="data.form.isDoubleFirstClass"
                :active-value="1"
                :inactive-value="0"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <!-- 基本信息 -->
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="英文名称">
              <el-input v-model="data.form.englishName" placeholder="如：Tsinghua University" clearable></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="创办时间">
              <el-input v-model="data.form.foundedYear" placeholder="如：1911年" clearable></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="隶属单位">
              <el-input v-model="data.form.affiliation" placeholder="如：教育部" clearable></el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 学校概况 -->
        <div class="form-section-title">学校概况</div>
        <el-form-item label="学校领导">
          <el-input v-model="data.form.leaderInfo" placeholder="如：校长 XXX 教授" clearable></el-input>
        </el-form-item>
        <el-form-item label="学校简介">
          <el-input v-model="data.form.schoolIntro" type="textarea" :rows="4" placeholder="请输入学校简介" clearable></el-input>
        </el-form-item>
        <el-form-item label="周边环境">
          <el-input v-model="data.form.campusEnvironment" type="textarea" :rows="3" placeholder="校园周边环境、交通、设施等情况" clearable></el-input>
        </el-form-item>

        <!-- 联系方式 -->
        <div class="form-section-title">联系方式</div>
        <el-form-item label="通讯地址">
          <el-input v-model="data.form.contactAddress" placeholder="请输入通讯地址" clearable></el-input>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="联系电话">
              <el-input v-model="data.form.contactPhone" placeholder="如：010-62785001" clearable></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="联系邮箱">
              <el-input v-model="data.form.contactEmail" placeholder="如：info@tsinghua.edu.cn" clearable></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="邮编">
              <el-input v-model="data.form.postcode" placeholder="如：100084" clearable></el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 学习生活 -->
        <div class="form-section-title">学习生活</div>
        <el-form-item label="图书馆">
          <el-input v-model="data.form.libraryInfo" placeholder="图书馆规模、藏书量、开放时间等" clearable></el-input>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="宿舍情况">
              <el-input v-model="data.form.dormitoryInfo" placeholder="宿舍条件、几人间等" clearable></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="食堂情况">
              <el-input v-model="data.form.canteenInfo" placeholder="食堂数量、菜品特色等" clearable></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="交通情况">
          <el-input v-model="data.form.transportInfo" placeholder="校内外交通情况，如：地铁直达、公交线路等" clearable></el-input>
        </el-form-item>

        <!-- 学科与考研 -->
        <div class="form-section-title">学科与考研</div>
        <el-form-item label="硕士点">
          <el-input v-model="data.form.masterProgramInfo" type="textarea" :rows="3" placeholder="硕士点数量及优势学科" clearable></el-input>
        </el-form-item>
        <el-form-item label="重点学科">
          <el-input v-model="data.form.keyDisciplineInfo" type="textarea" :rows="3" placeholder="国家级/省级重点学科" clearable></el-input>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="特色专业">
              <el-input v-model="data.form.featuredMajorInfo" placeholder="学校的特色优势专业" clearable></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="一流本科专业">
              <el-input v-model="data.form.firstClassMajorInfo" placeholder="双万计划一流本科专业" clearable></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="热门考研专业">
          <el-input v-model="data.form.graduateHotMajorInfo" placeholder="历年报考热度较高的专业方向" clearable></el-input>
        </el-form-item>

        <!-- 原字段保留 -->
        <div class="form-section-title">官方信息</div>
        <el-form-item prop="officialWebsite" label="官方网址">
          <el-input v-model="data.form.officialWebsite" placeholder="请输入官方网址"></el-input>
        </el-form-item>
        <el-form-item prop="description" label="学校简介(旧)">
          <el-input v-model="data.form.description" type="textarea" :rows="4" placeholder="原有简介字段，保留兼容"></el-input>
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
import defaultAvatar from "@/assets/imgs/avatar.png";

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
  provinceId: null,
  schoolType: null,
  educationLevel: null,
  is985: null,
  is211: null,
  isDoubleFirstClass: null,
  areasData: [],
  schoolTypeOptions: [
    "综合类",
    "理工类",
    "师范类",
    "财经类",
    "医药类",
    "农林类",
    "政法类",
    "艺术类",
    "语言类",
    "体育类",
  ],
  educationLevelOptions: ["本科", "专科"],
  ids: [],
  content: "",
  fromVisibleContent: false,
  rules: {
    name: [{ required: true, message: "请输入学校名称", trigger: "blur" }],
  },
});

const load = () => {
  request
    .get("/university/selectPage", {
      params: {
        pageNum: data.pageNum,
        pageSize: data.pageSize,
        name: data.name,
        provinceId: data.provinceId,
        schoolType: data.schoolType,
        educationLevel: data.educationLevel,
        is985: data.is985,
        is211: data.is211,
        isDoubleFirstClass: data.isDoubleFirstClass,
      },
    })
    .then((res) => {
      if (res.code === "200") {
        data.tableData = res.data?.list || [];
        data.total = res.data?.total;
      }
    });
};
const loadAreas = () => {
  request.get("/areas/selectAll").then((res) => {
    if (res.code === "200") {
      data.areasData = res.data || [];
    }
  });
};
const handleAdd = () => {
  data.form = {
    is985: 0,
    is211: 0,
    isDoubleFirstClass: 0,
  };
  data.formVisible = true;
};
const handleEdit = (row) => {
  data.form = JSON.parse(JSON.stringify(row));
  data.form.is985 = Number(data.form.is985 || 0);
  data.form.is211 = Number(data.form.is211 || 0);
  data.form.isDoubleFirstClass = Number(data.form.isDoubleFirstClass || 0);
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
  data.provinceId = null;
  data.schoolType = null;
  data.educationLevel = null;
  data.is985 = null;
  data.is211 = null;
  data.isDoubleFirstClass = null;
  load();
};

const preview = (content) => {
  data.content = content;
  data.fromVisibleContent = true;
};

loadAreas();
load();
</script>

<style scoped>
.form-section-title {
  font-size: 15px;
  font-weight: 700;
  color: #5B50E7;
  margin: 16px 0 10px;
  padding-left: 8px;
  border-left: 4px solid #5B50E7;
  line-height: 1.4;
}
</style>
