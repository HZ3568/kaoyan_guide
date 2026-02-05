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

    <div class="card" style="padding: 20px; margin-bottom: 10px">
      <div style="height: 400px" id="line"></div>
    </div>

    <div style="margin-bottom: 10px; display: flex; align-items: center; grid-gap: 10px">
      <div class="card" style="flex: 1; padding: 20px; height: 400px" id="pie"></div>
      <div class="card" style="flex: 1; padding: 20px; height: 400px" id="bar"></div>
    </div>

  </div>
</template>

<script setup>

import {reactive, onMounted} from "vue";
import request from "@/utils/request.js";
import {ElMessage} from "element-plus";
import * as echarts from 'echarts'

const lineOption = {
  title: {
    text: '近一周每日志愿填报人数的趋势图',
    subtext: '统计维度：每日志愿填报人数',
    left: 'center'
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    left: 'left'
  },
  xAxis: {
    type: 'category',
    name: '日期',
    data: []
  },
  yAxis: {
    type: 'value',
    name: '人数'
  },
  series: [
    {
      data: [],
      type: 'line',
      smooth: true,
      markPoint: {
        data: [
          { type: 'max', name: 'Max' },
          { type: 'min', name: 'Min' }
        ]
      },
      markLine: {
        data: [{ type: 'average', name: 'Avg' }]
      }
    },
  ]
}

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

const barOption = {
  title: {
    text: '不同门类志愿填报数量统计图',
    subtext: '统计维度：不同门类志愿填报数量',
    left: 'center'
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    left: 'left'
  },
  grid: {
    left: '15%',
    bottom:'10%'
  },
  xAxis: {
    type: 'category',
    name: '门类名称',
    data: [],
    axisLabel:{
      interval:0,
      rotate:-20   //值>0向右倾斜，值<0则向左倾斜
    }
  },
  yAxis: {
    type: 'value',
    name: '填报人数'
  },
  series: [
    {
      data: [],
      type: 'bar',
      smooth: true,
      itemStyle: {
        normal: {
          color: function(params) { // 根据索引返回对应的颜色
            let colorList = ['#ffaa2e','#32C5E9','#fa4c4c','#08b448','#FFDB5C','#ff9f7f','#fb7293','#E062AE','#E690D1','#e7bcf3']
            return colorList[params.dataIndex];
          }
        }
      },
    }
  ]
}

const data = reactive({
  user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
  count: {}
})

// 等页面所有元素加载完成后再设置 echarts图表
onMounted(() => {
  // 请求数据  初始化图表
  // 折线图
  let lineDom = document.getElementById('line');
  let lineChart = echarts.init(lineDom);
  request.get('/line').then(res => {
    lineOption.xAxis.data = res.data.x
    lineOption.series[0].data = res.data.y
    lineChart.setOption(lineOption)
  })

  // 饼图
  let pieDom = document.getElementById('pie');
  let pieChart = echarts.init(pieDom);
  request.get('/pie').then(res => {
    pieOption.series[0].data = res.data
    pieChart.setOption(pieOption)
  })

  // 柱状图
  let barDom = document.getElementById('bar');
  let barChart = echarts.init(barDom);
  request.get('/bar').then(res => {
    barOption.xAxis.data = res.data.nameList
    barOption.series[0].data = res.data.totalList
    barChart.setOption(barOption)
  })
})

request.get('/count').then(res => {
  data.count = res.data
})
</script>