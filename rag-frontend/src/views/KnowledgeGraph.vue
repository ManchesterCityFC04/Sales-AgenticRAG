<template>
  <div class="knowledge-graph-container">
    <!-- 页面头部 -->
    <div class="header">
      <div class="header-left">
        <el-button @click="goBack" type="primary" plain>
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h1 class="title">知识图谱</h1>
      </div>
      <div class="controls">
        <el-select
          v-model="selectedLabel"
          placeholder="选择标签"
          @change="loadGraphData"
          style="width: 200px; margin-right: 16px;"
        >
          <el-option label="全部" value="*" />
          <el-option
            v-for="label in availableLabels"
            :key="label"
            :label="label"
            :value="label"
          />
        </el-select>
        <el-button @click="refreshGraph" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 图谱容器 -->
    <div class="graph-container">
      <div
        ref="chartContainer"
        class="chart"
        v-loading="loading"
        element-loading-text="正在加载知识图谱..."
      ></div>
    </div>

    <!-- 统计信息 -->
    <div class="stats" v-if="graphStats">
      <div class="stat-item">
        <span class="label">节点数量:</span>
        <span class="value">{{ graphStats.nodeCount }}</span>
      </div>
      <div class="stat-item">
        <span class="label">关系数量:</span>
        <span class="value">{{ graphStats.edgeCount }}</span>
      </div>
      <div class="stat-item">
        <span class="label">标签类型:</span>
        <span class="value">{{ graphStats.labelCount }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, ArrowLeft } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { knowledgeAPI } from '@/api/knowledge.js'

// 响应式数据
const route = useRoute()
const router = useRouter()
const chartContainer = ref(null)
const loading = ref(false)
const selectedLabel = ref('*')
const availableLabels = ref([])
const graphStats = ref(null)

// ECharts实例
let chartInstance = null

// 获取知识库ID
const collectionId = route.params.collection_id || route.query.collection_id

// 加载图谱数据
const loadGraphData = async () => {
  if (!collectionId) {
    ElMessage.error('缺少知识库ID参数')
    return
  }

  loading.value = true
  try {
    const response = await knowledgeAPI.getKnowledgeGraph(collectionId, selectedLabel.value)
    const graphData = response.data || response
    
    // 处理图谱数据
    processGraphData(graphData)
    
    // 更新统计信息
    updateStats(graphData)
    
    // 渲染图谱
    renderGraph(graphData)
    
  } catch (error) {
    console.error('加载知识图谱失败:', error)
    ElMessage.error('加载知识图谱失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 处理图谱数据
const processGraphData = (data) => {
  // 提取所有可用的标签
  const labels = new Set()
  if (data.nodes) {
    data.nodes.forEach(node => {
      if (node.labels && Array.isArray(node.labels)) {
        node.labels.forEach(label => labels.add(label))
      }
    })
  }
  availableLabels.value = Array.from(labels).sort()
}

// 更新统计信息
const updateStats = (data) => {
  graphStats.value = {
    nodeCount: data.nodes ? data.nodes.length : 0,
    edgeCount: data.edges ? data.edges.length : 0,
    labelCount: availableLabels.value.length
  }
}

// 渲染图谱
const renderGraph = (data) => {
  if (!chartInstance || !data.nodes) return

  // 处理节点数据
  const nodes = data.nodes.map(node => ({
    id: node.id,
    name: node.properties?.entity_id || node.id,
    value: node.properties?.description || '',
    category: node.labels?.[0] || 'Unknown',
    symbolSize: Math.min(Math.max(20, (node.properties?.description?.length || 100) / 10), 80),
    itemStyle: {
      color: getNodeColor(node.labels?.[0])
    },
    label: {
      show: true,
      fontSize: 12
    }
  }))

  // 处理边数据
  const links = data.edges ? data.edges.map(edge => ({
    source: edge.source,
    target: edge.target,
    name: edge.type || 'RELATED',
    lineStyle: {
      color: '#999',
      width: 2
    }
  })) : []

  // 创建分类数据
  const categories = [...new Set(nodes.map(node => node.category))].map(cat => ({
    name: cat,
    itemStyle: {
      color: getNodeColor(cat)
    }
  }))

  // ECharts配置
  const option = {
    title: {
      text: `知识图谱 (${selectedLabel.value === '*' ? '全部' : selectedLabel.value})`,
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        if (params.dataType === 'node') {
          return `
            <div style="max-width: 300px;">
              <strong>${params.data.name}</strong><br/>
              <span style="color: #666;">类型: ${params.data.category}</span><br/>
              <div style="margin-top: 8px; max-height: 100px; overflow-y: auto;">
                ${params.data.value.substring(0, 200)}${params.data.value.length > 200 ? '...' : ''}
              </div>
            </div>
          `
        } else if (params.dataType === 'edge') {
          return `关系: ${params.data.name}`
        }
      }
    },
    legend: {
      show: false
    },
    series: [{
      name: '知识图谱',
      type: 'graph',
      layout: 'force',
      data: nodes,
      links: links,
      categories: categories,
      roam: true,
      focusNodeAdjacency: true,
      draggable: true,
      force: {
        repulsion: 1000,
        gravity: 0.1,
        edgeLength: [50, 200],
        layoutAnimation: true
      },
      label: {
        show: true,
        position: 'right',
        formatter: '{b}'
      },
      lineStyle: {
        color: 'source',
        curveness: 0.3
      },
      emphasis: {
        disabled: true
      }
    }]
  }

  chartInstance.setOption(option, true)
}

// 获取节点颜色
const getNodeColor = (category) => {
  const colors = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#ff9f7f'
  ]
  const hash = category ? category.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0)
    return a & a
  }, 0) : 0
  return colors[Math.abs(hash) % colors.length]
}

// 刷新图谱
const refreshGraph = () => {
  loadGraphData()
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 初始化图表
const initChart = async () => {
  await nextTick()
  if (chartContainer.value) {
    chartInstance = echarts.init(chartContainer.value)
    
    // 监听窗口大小变化
    window.addEventListener('resize', () => {
      chartInstance?.resize()
    })
  }
}

// 组件挂载
onMounted(async () => {
  await initChart()
  await loadGraphData()
})

// 组件卸载
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', () => {
    chartInstance?.resize()
  })
})
</script>

<style scoped>
.knowledge-graph-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.controls {
  display: flex;
  align-items: center;
}

.graph-container {
  flex: 1;
  padding: 20px;
  overflow: hidden;
}

.chart {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-item .label {
  color: #666;
  font-size: 14px;
}

.stat-item .value {
  color: #333;
  font-weight: bold;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .controls {
    justify-content: center;
  }
  
  .stats {
    flex-direction: column;
    gap: 12px;
    align-items: center;
  }
}
</style>