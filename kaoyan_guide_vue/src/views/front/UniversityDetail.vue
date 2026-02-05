<template>
  <div style="width: 60%; margin: 20px auto; min-height: 100vh">
    <div
      class="front-card"
      style="display: flex; grid-gap: 20px; margin-bottom: 20px"
    >
      <div style="width: 200px">
        <img
          :src="data.universityData.avatar"
          alt=""
          style="width: 100%; height: 200px"
        />
      </div>
      <div style="flex: 1">
        <div
          style="font-size: 24px; font-weight: bold; margin-bottom: 10px"
          class="line1"
        >
          {{ data.universityData.name }}
        </div>
        <div style="color: #666666ff; margin-bottom: 10px">
          教育行政主管部门：{{ data.universityData.department }}
        </div>
        <div style="color: #666666ff; margin-bottom: 10px">
          院校特性：{{ data.universityData.characters }}
        </div>
        <div style="color: #666666ff; margin-bottom: 10px">
          所在地：{{
            data.universityData.address || data.universityData.areasName
          }}
        </div>
        <div style="color: #666666ff; margin-bottom: 10px">
          详细地址：{{ data.universityData.address }}
        </div>
        <div style="color: #666666ff; margin-bottom: 10px">
          官方网址：{{ data.universityData.officialWebsite }}
        </div>
        <div style="color: #666666ff; margin-bottom: 10px">
          官方电话：{{ data.universityData.phone }}
        </div>
        <div style="color: #666666ff; margin-bottom: 10px">
          满意度：<el-rate
            v-model="data.universityData.mark"
            disabled
            show-score
            text-color="#ff9900"
            score-template="满意度{value}"
          />
        </div>
        <div style="display: flex; grid-gap: 10px; align-items: center">
          <el-button
            type="warning"
            @click="showComment"
            :disabled="data.universityData.commentFlag"
            >评价</el-button
          >
          <div style="color: red">（每人每个学校只能评价一次）</div>
        </div>
      </div>
      <div style="width: 100px">
        <div style="display: flex; grid-gap: 10px; align-items: center">
          <el-icon
            style="font-size: 24px; cursor: pointer"
            v-if="!data.universityData.collectFlag"
            @click="collectGoods(data.universityData.collectFlag)"
            ><Star
          /></el-icon>
          <div v-if="!data.universityData.collectFlag">收藏</div>
          <el-icon
            style="font-size: 24px; color: red; cursor: pointer"
            v-if="data.universityData.collectFlag"
            @click="collectGoods(data.universityData.collectFlag)"
            ><Star
          /></el-icon>
          <div v-if="data.universityData.collectFlag" style="color: red">
            取消收藏
          </div>
        </div>
      </div>
    </div>
    <div class="front-card" style="margin-bottom: 20px">
      <div
        style="
          display: flex;
          align-items: center;
          justify-content: center;
          grid-gap: 40px;
          margin-bottom: 20px;
        "
      >
        <div
          @click="changeCategory(item)"
          style="font-size: 18px; padding-bottom: 5px; cursor: pointer"
          :class="{ 'category-active': data.selectType === item }"
          v-for="item in data.activeCategory"
          :key="item"
        >
          {{ item }}
        </div>
      </div>
      <div v-if="data.selectType === '学校简介'">
        <div v-html="data.universityData.content"></div>
      </div>
      <div v-if="data.selectType === '专业介绍'">
        <div
          v-for="(categorysItem, index) in data.categorysList"
          :key="index"
          style="margin-bottom: 20px"
        >
          <div>
            <div
              style="
                width: 60px;
                padding-bottom: 10px;
                border-bottom: 3px solid #49c48d;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
              "
            >
              {{ categorysItem.name }}
            </div>
            <div style="display: flex; align-items: center">
              <span
                @click="changeSpecialtys(specialtysItem.id)"
                v-for="specialtysItem in data.specialtysList"
                :key="specialtysItem.id"
              >
                <div
                  class="specialtys-active"
                  v-if="specialtysItem.categorysId === categorysItem.id"
                  @click="
                    $router.push(
                      '/front/specialtysDetail?id=' + specialtysItem.id
                    )
                  "
                >
                  {{ specialtysItem.specialtysName }}
                </div>
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="data.selectType === '学校评价'" style="padding: 20px">
        <div
          style="margin-bottom: 20px"
          v-for="item in data.commentList"
          :key="item.id"
        >
          <div style="display: flex">
            <div style="width: 40px">
              <img
                :src="item.userAvatar"
                alt=""
                style="height: 40px; width: 40px; border-radius: 50%"
              />
            </div>
            <div style="margin-left: 10px">
              <div style="font-weight: 700; font-size: 17px; color: #000000ff">
                {{ item.userName }}
              </div>
              <div style="display: flex; align-items: center; grid-gap: 10px">
                <div style="color: #7a7a7aff">{{ item.time }}</div>
                <el-rate v-model="item.mark" disabled />
              </div>
            </div>
          </div>
          <div style="margin-top: 15px; font-size: 16px">
            {{ item.details }}
          </div>
        </div>
      </div>
    </div>
    <el-dialog
      title="学校评价"
      v-model="data.formVisible"
      width="40%"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :rules="data.rules"
        :model="data.form"
        label-width="80px"
        style="padding: 20px"
      >
        <el-form-item prop="details" label="评价内容">
          <el-input
            v-model="data.form.details"
            placeholder="请输入评价内容"
            type="textarea"
            rows="4"
          ></el-input>
        </el-form-item>
        <el-form-item prop="mark" label="评分">
          <el-rate v-model="data.form.mark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="data.formVisible = false">取 消</el-button>
          <el-button type="primary" @click="addComment">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, onMounted, ref } from "vue";
import request from "@/utils/request";
import { ElMessage, ElMessageBox } from "element-plus";
import { ChatDotRound } from "@element-plus/icons-vue";
import router from "@/router/index.js";
import { useRoute } from "vue-router";
const route = useRoute();
const formRef = ref();
const universityId = route.query.id;
const data = reactive({
  user: JSON.parse(localStorage.getItem("xm-user") || "{}"),
  universityData: {},
  formVisible: false,
  form: {},
  selectType: "学校简介",
  activeCategory: ["学校简介", "专业介绍", "学校评价"],
  specialtysList: [],
  categorysList: [],
  commentList: [],
  activeCategoryId: null,
  rules: {
    details: [{ required: true, message: "请输入评价内容", trigger: "blur" }],
    mark: [{ required: true, message: "请选择评分", trigger: "blur" }],
  },
});
onMounted(() => {
  loadUniversity();
});
const loadUniversity = () => {
  request
    .get("/university/selectByUniversityId/" + universityId)
    .then((res) => {
      if (res.code === "200") {
        data.universityData = res.data;
      } else {
        ElMessage.error(res.msg);
      }
    });
};

const collectGoods = (flag) => {
  let dataForm = {
    universityId: data.universityData.id,
    userId: data.user.id,
  };
  request.post("/collect/collectUniversity", dataForm).then((res) => {
    if (res.code === "200") {
      loadUniversity();
      if (!flag) {
        ElMessage.success("已收藏");
      } else {
        ElMessage.success("已取消收藏");
      }
    } else {
      ElMessage.error(res.msg);
    }
  });
};
const loadCategorys = () => {
  request.get("/categorys/selectAll").then((res) => {
    if (res.code === "200") {
      data.categorysList = res.data;
    } else {
      ElMessage.error(res.msg);
    }
  });
};
loadCategorys();

const loadUniversitySpecialtys = () => {
  request
    .get("/universitySpecialtys/selectAll", {
      params: {
        universityId: universityId,
      },
    })
    .then((res) => {
      if (res.code === "200") {
        data.specialtysList = res.data;
      } else {
        ElMessage.error(res.msg);
      }
    });
};
loadUniversitySpecialtys();

const changeCategory = (item) => {
  data.selectType = item;
};

const changeSpecialtys = (id) => {
  data.activeCategoryId = id;
};

const showComment = () => {
  data.formVisible = true;
};

const addComment = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      data.form.userId = data.user.id;
      data.form.universityId = universityId;
      request.post("/comment/add", data.form).then((res) => {
        if (res.code === "200") {
          data.formVisible = false;
          ElMessage.success("评价成功");
          loadUniversity();
          loadComment();
        } else {
          ElMessage.error(res.msg);
        }
      });
    }
  });
};

const loadComment = () => {
  request
    .get("/comment/selectAll", {
      params: {
        universityId: universityId,
      },
    })
    .then((res) => {
      if (res.code === "200") {
        data.commentList = res.data;
      } else {
        ElMessage.error(res.msg);
      }
    });
};
loadComment();
</script>

<style scoped>
.category-active {
  color: #49c48d;
  border-bottom: 2px solid #49c48d;
  font-weight: bold;
}

.specialtys-active {
  padding-bottom: 5px;
  margin-right: 20px;
  cursor: pointer;
}

.specialtys-active:hover {
  padding-bottom: 5px;
  margin-right: 20px;
  color: #49c48d;
  cursor: pointer;
}
</style>
