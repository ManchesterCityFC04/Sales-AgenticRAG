<template>
  <div class="sales-mode-panel">
    <!-- 销售模式开关和场景选择 -->
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center space-x-4">
        <!-- 销售模式开关 -->
        <div class="flex items-center space-x-2">
          <label class="flex items-center cursor-pointer">
            <input
              type="checkbox"
              :checked="salesMode"
              @change="$emit('update:salesMode', $event.target.checked)"
              class="sr-only peer"
            />
            <div
              class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
            ></div>
            <span class="ml-2 text-sm font-medium text-gray-700">销售模式</span>
          </label>
        </div>

        <!-- 场景选择 -->
        <div v-if="salesMode" class="flex items-center space-x-2">
          <span class="text-sm text-gray-600">场景:</span>
          <select
            :value="scenario"
            @change="$emit('update:scenario', $event.target.value)"
            class="text-sm border border-gray-300 rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="automotive">🚗 汽车销售</option>
            <option value="real_estate">🏠 房地产</option>
            <option value="insurance">🛡️ 保险</option>
            <option value="retail">🛍️ 零售</option>
          </select>
        </div>
      </div>

      <!-- 状态指示器 -->
      <div v-if="salesMode" class="flex items-center space-x-2">
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <span class="w-2 h-2 mr-1.5 bg-green-400 rounded-full animate-pulse"></span>
          销售模式已启用
        </span>
      </div>
    </div>

    <!-- 销售信息卡片 -->
    <div v-if="salesMode && hasSalesInfo" class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
      <div class="space-y-2">
        <!-- 销售意图 -->
        <div v-if="salesInfo.intent" class="flex items-start">
          <span class="text-xs font-medium text-blue-700 mr-2">🎯 意图:</span>
          <span class="text-xs text-blue-900">{{ getIntentText(salesInfo.intent) }}</span>
        </div>

        <!-- 客户需求 -->
        <div v-if="salesInfo.customer_needs && salesInfo.customer_needs.key_concerns" class="flex items-start">
          <span class="text-xs font-medium text-blue-700 mr-2">📊 关注:</span>
          <span class="text-xs text-blue-900">{{ salesInfo.customer_needs.key_concerns.join('、') }}</span>
        </div>

        <!-- 产品推荐 -->
        <div v-if="salesInfo.product_recommendation && salesInfo.product_recommendation.product_name" class="flex items-start">
          <span class="text-xs font-medium text-blue-700 mr-2">💡 推荐:</span>
          <span class="text-xs text-blue-900">{{ salesInfo.product_recommendation.product_name }}</span>
        </div>

        <!-- 销售话术预览 -->
        <div v-if="salesInfo.sales_script" class="flex items-start">
          <span class="text-xs font-medium text-blue-700 mr-2">💬 话术:</span>
          <span class="text-xs text-blue-900 line-clamp-2">{{ salesInfo.sales_script }}</span>
        </div>
      </div>
    </div>

    <!-- 提示信息 -->
    <div v-if="salesMode && !hasSalesInfo" class="mt-3 p-2 bg-gray-50 border border-gray-200 rounded-lg">
      <p class="text-xs text-gray-600">
        💡 销售模式已启用，系统将自动识别客户意图、分析需求并提供专业的销售话术
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  salesMode: {
    type: Boolean,
    default: false
  },
  scenario: {
    type: String,
    default: 'automotive'
  },
  salesInfo: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:salesMode', 'update:scenario'])

// 判断是否有销售信息
const hasSalesInfo = computed(() => {
  return props.salesInfo && Object.keys(props.salesInfo).length > 0
})

// 获取意图文本
const getIntentText = (intent) => {
  const intentMap = {
    'product_inquiry': '产品咨询',
    'price_negotiation': '价格谈判',
    'competitor_comparison': '竞品对比',
    'objection_handling': '异议处理',
    'chitchat': '闲聊寒暄',
    'test_drive_booking': '预约试驾'
  }
  return intentMap[intent] || intent
}
</script>

<style scoped>
.sales-mode-panel {
  @apply transition-all duration-200;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 开关动画 */
input[type="checkbox"]:checked + div {
  @apply bg-blue-600;
}

/* 脉冲动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
