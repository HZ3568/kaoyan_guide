<template>
  <div>
    <div style="margin-bottom: 10px">
      <div style="display: flex; align-items: center; grid-gap: 10px">
        <div class="card" style="flex: 1; padding: 20px; display: flex; align-items: center; grid-gap: 20px">
          <img style="width: 80px; height: 80px" src="@/assets/imgs/门类.png" alt="">
          <div style="flex: 1; font-size: 20px">
            <div style="margin-bottom: 10px">门类数量</div>
            <div style="font-weight: bold">{{ data.count.categorysNumber || 0 }}</div>
          </div>
        </div>
        <div class="card" style="flex: 1; padding: 20px; display: flex; align-items: center; grid-gap: 20px">
          <img style="width: 80px; height: 80px" src="@/assets/imgs/专业.png" alt="">
          <div style="flex: 1; font-size: 20px">
            <div style="margin-bottom: 10px">专业数量</div>
            <div style="font-weight: bold">{{ data.count.specialtysNumber || 0  }}</div>
          </div>
        </div>

        <div class="card" style="flex: 1; padding: 20px; display: flex; align-items: center; grid-gap: 20px">
          <img style="width: 80px; height: 80px" src="@/assets/imgs/大学.png" alt="">
          <div style="flex: 1; font-size: 20px">
            <div style="margin-bottom: 10px">认证大学</div>
            <div style="font-weight: bold">{{ data.count.universityNumber || 0  }}</div>
          </div>
        </div>

        <div class="card" style="flex: 1; padding: 20px; display: flex; align-items: center; grid-gap: 20px">
          <img style="width: 80px; height: 80px" src="@/assets/imgs/学生.png" alt="">
          <div style="flex: 1; font-size: 20px">
            <div style="margin-bottom: 10px">认证学生</div>
            <div style="font-weight: bold">{{ data.count.userNumber || 0  }}</div>
          </div>
        </div>

      </div>
    </div>

    <div style="margin-bottom: 10px">
      <div class="card" style="padding: 20px; height: 400px" id="pie"></div>
    </div>

  </div>
</template>

<script setup>

import {reactive, onMounted} from "vue";
import request from "@/utils/request.js";
import * as echarts from 'echarts'

const pieOption = {
  title: {
    text: '不同门类专业数量分布图',
    subtext: '统计维度：不同门类专业数量',
    left: 'center'
  },
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      type: 'pie',
      center: ['50%', '60%'],
      radius: '60%',
      data: [],
      label: {
        show: true,
        formatter(param) {
          return param.name + ' (' + param.percent + '%)';
        }
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}

const data = reactive({
  user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
  count: {}
})

// 等页面所有元素加载完成后再设置 echarts图表
onMounted(() => {
  let pieDom = document.getElementById('pie');
  let pieChart = echarts.init(pieDom);
  request.get('/pie').then(res => {
    pieOption.series[0].data = res.data
    pieChart.setOption(pieOption)
  })
})

request.get('/count').then(res => {
  data.count = res.data
})
</script>
