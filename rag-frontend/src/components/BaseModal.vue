<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click="handleBackdropClick"
      >
        <!-- 背景遮罩 -->
        <div
          class="absolute inset-0 bg-gray-900 bg-opacity-50 transition-opacity"
        ></div>

        <!-- 模态框内容 -->
        <div
          :class="modalClasses"
          class="relative bg-white rounded-xl shadow-[0_4px_16px_rgba(0,0,0,0.12)] border border-gray-100 animate-scale-in"
          @click.stop
        >
          <!-- 关闭按钮 -->
          <button
            v-if="showClose"
            class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
            @click="close"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <!-- 模态框头部 -->
          <div v-if="$slots.header || title" class="px-6 pt-6 pb-4 border-b border-gray-100">
            <slot name="header">
              <h3 class="text-xl font-normal text-gray-900">{{ title }}</h3>
            </slot>
          </div>

          <!-- 模态框内容 -->
          <div :class="contentPaddingClass">
            <slot></slot>
          </div>

          <!-- 模态框底部 -->
          <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-100 flex items-center justify-end space-x-3">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, watch } from 'vue'

const props = defineProps({
  // v-model绑定
  modelValue: {
    type: Boolean,
    required: true
  },
  // 模态框标题
  title: {
    type: String,
    default: ''
  },
  // 是否显示关闭按钮
  showClose: {
    type: Boolean,
    default: true
  },
  // 点击背景是否关闭
  closeOnClickOutside: {
    type: Boolean,
    default: true
  },
  // 模态框大小
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl', '2xl'].includes(value)
  },
  // 是否有内边距
  contentPadding: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const modalClasses = computed(() => {
  const sizeClasses = {
    sm: 'w-full max-w-sm',
    md: 'w-full max-w-md',
    lg: 'w-full max-w-lg',
    xl: 'w-full max-w-xl',
    '2xl': 'w-full max-w-2xl'
  }
  return sizeClasses[props.size]
})

const contentPaddingClass = computed(() => {
  return props.contentPadding ? 'px-6 py-4' : ''
})

const close = () => {
  emit('update:modelValue', false)
  emit('close')
}

const handleBackdropClick = () => {
  if (props.closeOnClickOutside) {
    close()
  }
}

// 监听模态框打开/关闭，控制body滚动
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>
