<template>
  <div class="flex flex-col items-center justify-center py-12 px-4">
    <!-- 图标 -->
    <div :class="iconContainerClasses">
      <slot name="icon">
        <!-- 默认空状态图标 -->
        <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
      </slot>
    </div>

    <!-- 标题 -->
    <h3 class="mt-4 text-lg font-medium text-gray-900">
      <slot name="title">
        {{ title }}
      </slot>
    </h3>

    <!-- 描述 -->
    <p v-if="description || $slots.description" class="mt-2 text-sm text-gray-500 text-center max-w-sm">
      <slot name="description">
        {{ description }}
      </slot>
    </p>

    <!-- 操作按钮 -->
    <div v-if="$slots.action" class="mt-6">
      <slot name="action"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 标题
  title: {
    type: String,
    default: '暂无数据'
  },
  // 描述
  description: {
    type: String,
    default: ''
  },
  // 图标类型
  iconType: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'search', 'file', 'message'].includes(value)
  }
})

const iconContainerClasses = computed(() => {
  return 'w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center'
})
</script>
