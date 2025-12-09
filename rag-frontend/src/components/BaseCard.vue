<template>
  <div :class="cardClasses" @click="handleClick">
    <!-- 卡片头部 -->
    <div v-if="$slots.header || title" class="border-b border-gray-200 pb-4 mb-4">
      <slot name="header">
        <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
      </slot>
    </div>

    <!-- 卡片内容 -->
    <div :class="contentClasses">
      <slot></slot>
    </div>

    <!-- 卡片底部 -->
    <div v-if="$slots.footer" class="border-t border-gray-200 pt-4 mt-4">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 卡片标题
  title: {
    type: String,
    default: ''
  },
  // 是否有悬停效果
  hover: {
    type: Boolean,
    default: false
  },
  // 是否有内边距
  padding: {
    type: Boolean,
    default: true
  },
  // 是否可点击
  clickable: {
    type: Boolean,
    default: false
  },
  // 自定义class
  customClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['click'])

const cardClasses = computed(() => {
  const classes = ['card']

  if (props.hover) classes.push('card-hover')
  if (props.padding) classes.push('card-padding')
  if (props.clickable) classes.push('cursor-pointer')
  if (props.customClass) classes.push(props.customClass)

  return classes
})

const contentClasses = computed(() => {
  return props.padding ? '' : 'p-0'
})

const handleClick = (event) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>
