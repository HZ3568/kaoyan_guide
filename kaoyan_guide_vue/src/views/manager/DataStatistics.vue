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
            <div style="margin-bottom: 10px">院校总数</div>
            <div style="font-weight: bold">{{ data.count.universityNumber || 0  }}</div>
          </div>
        </div>

        <div class="card" style="flex: 1; padding: 20px; display: flex; align-items: center; grid-gap: 20px">
          <img style="width: 80px; height: 80px" src="@/assets/imgs/学生.png" alt="">
          <div style="flex: 1; font-size: 20px">
            <div style="margin-bottom: 10px">注册用户</div>
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
    text: '各门类专业数量分布',
    subtext: '当前系统各门类下收录的专业数量统计',
    left: 'center',
    textStyle: { fontSize: 16, fontWeight: 600, color: '#333' },
    subtextStyle: { fontSize: 12, color: '#999' },
    top: 10
  },
  tooltip: {
    trigger: 'item',
    formatter(param) {
      return `<b>${param.name}</b><br/>专业数量：${param.value} 个<br/>占比：${param.percent}%`;
    }
  },
  legend: {
    orient: 'horizontal',
    bottom: 10,
    left: 'center',
    itemGap: 20,
    textStyle: { color: '#666', fontSize: 12 }
  },
  series: [
    {
      type: 'pie',
      center: ['50%', '50%'],
      radius: ['35%', '60%'],
      data: [],
      label: {
        show: true,
        formatter(param) {
          return param.name + '\n' + param.value + '个';
        },
        fontSize: 11,
        color: '#666',
        lineHeight: 18
      },
      labelLine: { show: true, length: 8, length2: 6 },
      emphasis: {
        itemStyle: {
          shadowBlur: 12,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.2)'
        },
        label: { show: true, fontSize: 13, fontWeight: 600 }
      },
      itemStyle: {
        borderRadius: 6,
        borderColor: '#fff',
        borderWidth: 2
      }
    }
  ]
}

const data = reactive({
  user: JSON.parse(localStorage.getItem('xm-admin') || '{}'),
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
