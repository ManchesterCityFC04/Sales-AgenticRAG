<template>
  <div :class="containerClasses">
    <!-- 头像 -->
    <div v-if="showAvatar" class="flex-shrink-0">
      <div :class="avatarClasses">
        <!-- 用户头像 - 显示首字母 -->
        <span v-if="role === 'user'" class="text-white font-medium">
          {{ avatarText }}
        </span>
        <!-- AI头像 - 显示机器人图标 -->
        <svg v-else class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>
    </div>

    <!-- 消息内容 -->
    <div class="flex-1">
      <!-- 消息发送者和时间 -->
      <div v-if="showHeader" class="flex items-center space-x-2 mb-1">
        <span class="text-sm font-medium text-gray-700">
          {{ senderName }}
        </span>
        <span v-if="timestamp" class="text-xs text-gray-500">
          {{ formattedTime }}
        </span>
      </div>

      <!-- 消息气泡 -->
      <div :class="bubbleClasses">
        <slot>
          <p class="whitespace-pre-wrap break-words">{{ content }}</p>
        </slot>
      </div>

      <!-- 消息状态 -->
      <div v-if="showStatus" class="mt-1 flex items-center space-x-1 text-xs text-gray-500">
        <!-- 发送中 -->
        <svg v-if="status === 'sending'" class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <!-- 已发送 -->
        <svg v-else-if="status === 'sent'" class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
        <!-- 错误 -->
        <svg v-else-if="status === 'error'" class="w-3 h-3 text-danger-500" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <span>{{ statusText }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 消息角色：user 或 assistant
  role: {
    type: String,
    required: true,
    validator: (value) => ['user', 'assistant'].includes(value)
  },
  // 消息内容
  content: {
    type: String,
    default: ''
  },
  // 发送者名称
  senderName: {
    type: String,
    default: ''
  },
  // 时间戳
  timestamp: {
    type: [String, Number, Date],
    default: null
  },
  // 消息状态：sending, sent, error
  status: {
    type: String,
    default: 'sent',
    validator: (value) => ['sending', 'sent', 'error'].includes(value)
  },
  // 是否显示头像
  showAvatar: {
    type: Boolean,
    default: true
  },
  // 是否显示消息头部（发送者和时间）
  showHeader: {
    type: Boolean,
    default: false
  },
  // 是否显示状态
  showStatus: {
    type: Boolean,
    default: false
  }
})

const containerClasses = computed(() => {
  const baseClasses = 'flex gap-3 mb-4'
  return props.role === 'user'
    ? `${baseClasses} flex-row-reverse`
    : baseClasses
})

const avatarClasses = computed(() => {
  const baseClasses = 'w-8 h-8 rounded-full flex items-center justify-center'
  return props.role === 'user'
    ? `${baseClasses} bg-gray-900`
    : `${baseClasses} bg-gray-100`
})

const bubbleClasses = computed(() => {
  return props.role === 'user'
    ? 'message-bubble message-bubble-user'
    : 'message-bubble message-bubble-assistant'
})

const avatarText = computed(() => {
  if (props.senderName) {
    return props.senderName.charAt(0).toUpperCase()
  }
  return 'U'
})

const formattedTime = computed(() => {
  if (!props.timestamp) return ''

  const date = new Date(props.timestamp)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const statusText = computed(() => {
  const statusMap = {
    sending: '发送中...',
    sent: '已发送',
    error: '发送失败'
  }
  return statusMap[props.status] || ''
})
</script>
