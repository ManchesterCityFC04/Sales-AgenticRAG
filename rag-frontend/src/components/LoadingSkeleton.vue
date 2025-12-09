<template>
  <div :class="containerClasses">
    <!-- 文本骨架屏 -->
    <div v-if="type === 'text'" class="space-y-3">
      <div v-for="n in rows" :key="n" :class="skeletonClasses" :style="getRowStyle(n)"></div>
    </div>

    <!-- 卡片骨架屏 -->
    <div v-else-if="type === 'card'" class="card card-padding space-y-4">
      <!-- 头部 -->
      <div class="flex items-center space-x-3">
        <div class="w-12 h-12 bg-gray-200 rounded-full animate-pulse"></div>
        <div class="flex-1 space-y-2">
          <div class="h-4 bg-gray-200 rounded animate-pulse w-1/3"></div>
          <div class="h-3 bg-gray-200 rounded animate-pulse w-1/2"></div>
        </div>
      </div>
      <!-- 内容 -->
      <div class="space-y-2">
        <div class="h-3 bg-gray-200 rounded animate-pulse"></div>
        <div class="h-3 bg-gray-200 rounded animate-pulse w-5/6"></div>
        <div class="h-3 bg-gray-200 rounded animate-pulse w-4/6"></div>
      </div>
    </div>

    <!-- 列表骨架屏 -->
    <div v-else-if="type === 'list'" class="space-y-4">
      <div v-for="n in rows" :key="n" class="flex items-center space-x-3">
        <div v-if="avatar" class="w-10 h-10 bg-gray-200 rounded-full animate-pulse"></div>
        <div class="flex-1 space-y-2">
          <div class="h-4 bg-gray-200 rounded animate-pulse" :style="`width: ${Math.random() * 30 + 60}%`"></div>
          <div class="h-3 bg-gray-200 rounded animate-pulse" :style="`width: ${Math.random() * 20 + 40}%`"></div>
        </div>
      </div>
    </div>

    <!-- 自定义骨架屏 -->
    <div v-else :class="skeletonClasses"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 骨架屏类型
  type: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'card', 'list', 'custom'].includes(value)
  },
  // 行数
  rows: {
    type: Number,
    default: 3
  },
  // 是否显示头像（list类型）
  avatar: {
    type: Boolean,
    default: true
  },
  // 是否有动画
  animated: {
    type: Boolean,
    default: true
  },
  // 自定义类名
  customClass: {
    type: String,
    default: ''
  }
})

const containerClasses = computed(() => {
  return props.customClass
})

const skeletonClasses = computed(() => {
  const classes = ['bg-gray-200 rounded']
  if (props.animated) classes.push('animate-pulse')
  if (props.type === 'text') classes.push('h-4')
  if (props.type === 'custom') classes.push('h-32')
  return classes
})

const getRowStyle = (rowNumber) => {
  // 最后一行可能较短
  if (rowNumber === props.rows) {
    return { width: `${Math.random() * 30 + 50}%` }
  }
  return {}
}
</script>
