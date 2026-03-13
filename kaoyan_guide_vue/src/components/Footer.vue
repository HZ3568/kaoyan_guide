<template>
  <div>
    <div style="padding: 20px; background-color: #282828; color: #ababab;">
      <div style="
          width: 80%;
          margin: 20px auto;
          display: flex;
          justify-content: flex-start;
          align-items: flex-start;
          gap: 160px;
          flex-wrap: wrap;
        ">
        <!-- 左侧 -->
        <div style="display: flex; align-items: center; min-width: 260px;">
          <img
            src="@/assets/imgs/logo.png"
            alt="logo"
            style="height: 70px; margin-right: 16px;"
          />
          <div>
            <div style="font-size: 24px; font-weight: bold; color: #ffffff;">
              研途规划
            </div>
            <div style="font-size: 14px; color: #888; margin-top: 6px;">
              考研学习规划与资源整合平台
            </div>
          </div>
        </div>

        <!-- 右侧 -->
        <div style="text-align: left; line-height: 28px; font-size: 14px; max-width: 720px;">
          <div>本平台为本科毕业设计项目演示系统，仅用于学习、交流与功能展示。</div>
          <div>项目名称：考研学习规划与资源整合平台</div>
          <div>开发者：董寒</div>
          <div>所属学院：信息科学与工程学院</div>
          <div>所属专业：软件工程专业</div>
          <div>学校：临沂大学</div>
          <div>COPYRIGHT © 2026 YANTU GUIDE. ALL RIGHTS RESERVED.</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({});
</script>