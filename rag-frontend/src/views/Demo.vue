<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-6xl mx-auto">
      <!-- 页面标题 -->
      <div class="mb-8 text-center">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">RAG 设计系统演示</h1>
        <p class="text-gray-600">查看所有新组件和样式的效果</p>
      </div>

      <!-- 按钮组件演示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">按钮组件 (BaseButton)</h2>
        <div class="card card-padding space-y-4">
          <!-- 按钮变体 -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-3">按钮变体</h3>
            <div class="flex flex-wrap gap-3">
              <BaseButton variant="primary">主要按钮</BaseButton>
              <BaseButton variant="secondary">次要按钮</BaseButton>
              <BaseButton variant="success">成功按钮</BaseButton>
              <BaseButton variant="danger">危险按钮</BaseButton>
              <BaseButton variant="ghost">幽灵按钮</BaseButton>
            </div>
          </div>

          <!-- 按钮大小 -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-3">按钮大小</h3>
            <div class="flex flex-wrap items-center gap-3">
              <BaseButton variant="primary" size="sm">小按钮</BaseButton>
              <BaseButton variant="primary" size="md">中等按钮</BaseButton>
              <BaseButton variant="primary" size="lg">大按钮</BaseButton>
            </div>
          </div>

          <!-- 按钮状态 -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-3">按钮状态</h3>
            <div class="flex flex-wrap gap-3">
              <BaseButton variant="primary" :loading="true">加载中...</BaseButton>
              <BaseButton variant="primary" :disabled="true">禁用按钮</BaseButton>
              <BaseButton variant="primary" block>全宽按钮</BaseButton>
            </div>
          </div>

          <!-- 带图标的按钮 -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-3">带图标按钮</h3>
            <div class="flex flex-wrap gap-3">
              <BaseButton variant="primary">
                <template #icon>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                </template>
                添加
              </BaseButton>
              <BaseButton variant="danger">
                <template #icon>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </template>
                删除
              </BaseButton>
            </div>
          </div>
        </div>
      </section>

      <!-- 卡片组件演示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">卡片组件 (BaseCard)</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 基本卡片 -->
          <BaseCard title="基本卡片">
            <p class="text-gray-600">这是一个基本的卡片组件，带有标题和内容区域。</p>
          </BaseCard>

          <!-- 可悬停卡片 -->
          <BaseCard title="可悬停卡片" :hover="true">
            <p class="text-gray-600">鼠标悬停时会有阴影和上浮效果。</p>
          </BaseCard>

          <!-- 可点击卡片 -->
          <BaseCard title="可点击卡片" :hover="true" :clickable="true" @click="handleCardClick">
            <p class="text-gray-600">点击我试试！可以添加点击事件。</p>
          </BaseCard>
        </div>

        <!-- 自定义头部和底部的卡片 -->
        <div class="mt-6">
          <BaseCard>
            <template #header>
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900">自定义头部</h3>
                <span class="badge badge-primary">新</span>
              </div>
            </template>

            <p class="text-gray-600 mb-4">这个卡片使用了自定义的头部和底部插槽。</p>
            <p class="text-gray-600">可以在头部和底部放置任何自定义内容。</p>

            <template #footer>
              <div class="flex justify-end space-x-2">
                <BaseButton variant="secondary" size="sm">取消</BaseButton>
                <BaseButton variant="primary" size="sm">确认</BaseButton>
              </div>
            </template>
          </BaseCard>
        </div>
      </section>

      <!-- 模态框演示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">模态框组件 (BaseModal)</h2>
        <div class="card card-padding">
          <div class="flex flex-wrap gap-3">
            <BaseButton variant="primary" @click="showSmallModal = true">小模态框</BaseButton>
            <BaseButton variant="primary" @click="showMediumModal = true">中等模态框</BaseButton>
            <BaseButton variant="primary" @click="showLargeModal = true">大模态框</BaseButton>
          </div>

          <!-- 小模态框 -->
          <BaseModal v-model="showSmallModal" title="小模态框" size="sm">
            <p class="text-gray-600">这是一个小尺寸的模态框。</p>
            <template #footer>
              <BaseButton variant="secondary" @click="showSmallModal = false">关闭</BaseButton>
            </template>
          </BaseModal>

          <!-- 中等模态框 -->
          <BaseModal v-model="showMediumModal" title="中等模态框" size="md">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">姓名</label>
                <input type="text" class="input" placeholder="请输入姓名" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
                <input type="email" class="input" placeholder="请输入邮箱" />
              </div>
            </div>
            <template #footer>
              <BaseButton variant="secondary" @click="showMediumModal = false">取消</BaseButton>
              <BaseButton variant="primary" @click="showMediumModal = false">提交</BaseButton>
            </template>
          </BaseModal>

          <!-- 大模态框 -->
          <BaseModal v-model="showLargeModal" title="大模态框" size="lg">
            <p class="text-gray-600 mb-4">这是一个大尺寸的模态框，可以容纳更多内容。</p>
            <p class="text-gray-600">模态框支持多种尺寸：sm、md、lg、xl、2xl。</p>
            <template #footer>
              <BaseButton variant="primary" @click="showLargeModal = false">知道了</BaseButton>
            </template>
          </BaseModal>
        </div>
      </section>

      <!-- 消息气泡演示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">消息气泡组件 (MessageBubble)</h2>
        <div class="card card-padding space-y-4">
          <!-- 用户消息 -->
          <MessageBubble
            role="user"
            content="你好！这是一条用户发送的消息。"
            sender-name="张三"
            :timestamp="Date.now() - 60000"
            :show-avatar="true"
            :show-header="true"
          />

          <!-- AI消息 -->
          <MessageBubble
            role="assistant"
            content="您好！我是AI助手。这是一条AI回复的消息。消息气泡支持显示头像、时间戳和消息状态。"
            sender-name="AI助手"
            :timestamp="Date.now() - 30000"
            :show-avatar="true"
            :show-header="true"
          />

          <!-- 发送中的消息 -->
          <MessageBubble
            role="user"
            content="这是一条正在发送的消息..."
            status="sending"
            :show-avatar="true"
            :show-status="true"
          />

          <!-- 使用插槽自定义内容 -->
          <MessageBubble role="assistant" :show-avatar="true">
            <div class="space-y-2">
              <p class="font-semibold">这是使用插槽自定义的消息内容：</p>
              <ul class="list-disc list-inside space-y-1">
                <li>支持自定义HTML内容</li>
                <li>可以渲染Markdown</li>
                <li>灵活的内容展示</li>
              </ul>
            </div>
          </MessageBubble>
        </div>
      </section>

      <!-- 加载骨架屏演示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">加载骨架屏 (LoadingSkeleton)</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 文本骨架屏 -->
          <div class="card card-padding">
            <h3 class="text-sm font-medium text-gray-700 mb-3">文本骨架屏</h3>
            <LoadingSkeleton type="text" :rows="4" />
          </div>

          <!-- 卡片骨架屏 -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-3">卡片骨架屏</h3>
            <LoadingSkeleton type="card" />
          </div>

          <!-- 列表骨架屏 -->
          <div class="md:col-span-2">
            <h3 class="text-sm font-medium text-gray-700 mb-3">列表骨架屏</h3>
            <div class="card card-padding">
              <LoadingSkeleton type="list" :rows="3" :avatar="true" />
            </div>
          </div>
        </div>
      </section>

      <!-- 空状态演示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">空状态组件 (EmptyState)</h2>
        <div class="card card-padding">
          <EmptyState
            title="暂无数据"
            description="当前没有任何数据，点击下方按钮开始创建。"
          >
            <template #action>
              <BaseButton variant="primary" @click="handleCreate">
                <template #icon>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                </template>
                创建新项目
              </BaseButton>
            </template>
          </EmptyState>
        </div>
      </section>

      <!-- 全局样式类演示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">全局样式类</h2>
        <div class="card card-padding space-y-6">
          <!-- 徽章 -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-3">徽章</h3>
            <div class="flex flex-wrap gap-2">
              <span class="badge badge-primary">Primary</span>
              <span class="badge badge-success">Success</span>
              <span class="badge badge-warning">Warning</span>
              <span class="badge badge-danger">Danger</span>
              <span class="badge badge-info">Info</span>
            </div>
          </div>

          <!-- 输入框 -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-3">输入框</h3>
            <div class="space-y-3">
              <input type="text" class="input" placeholder="普通输入框" />
              <input type="text" class="input input-error" placeholder="错误状态输入框" />
              <input type="text" class="input" placeholder="禁用输入框" disabled />
            </div>
          </div>

          <!-- 文本省略 -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-3">文本省略</h3>
            <div class="space-y-2">
              <p class="text-ellipsis-2 text-gray-600">
                这是一段很长的文本，用于演示两行省略的效果。当文本超过两行时，会自动显示省略号。这是一段很长的文本，用于演示两行省略的效果。当文本超过两行时，会自动显示省略号。
              </p>
            </div>
          </div>

          <!-- 渐变效果 -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-3">渐变效果</h3>
            <div class="space-y-3">
              <div class="h-20 rounded-lg gradient-primary flex items-center justify-center text-white font-semibold">
                渐变背景
              </div>
              <h1 class="text-4xl font-bold gradient-text">渐变文字效果</h1>
            </div>
          </div>
        </div>
      </section>

      <!-- 动画演示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">动画效果</h2>
        <div class="card card-padding">
          <BaseButton variant="primary" @click="triggerAnimations">
            <template #icon>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </template>
            重新播放动画
          </BaseButton>

          <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div v-if="showAnimations" class="card card-padding animate-fade-in">
              <div class="text-center">
                <div class="w-12 h-12 bg-primary-600 rounded-full mx-auto mb-2"></div>
                <p class="text-sm text-gray-600">淡入动画</p>
              </div>
            </div>

            <div v-if="showAnimations" class="card card-padding animate-fade-in-up animation-delay-100">
              <div class="text-center">
                <div class="w-12 h-12 bg-success-600 rounded-full mx-auto mb-2"></div>
                <p class="text-sm text-gray-600">向上淡入</p>
              </div>
            </div>

            <div v-if="showAnimations" class="card card-padding animate-scale-in animation-delay-200">
              <div class="text-center">
                <div class="w-12 h-12 bg-warning-600 rounded-full mx-auto mb-2"></div>
                <p class="text-sm text-gray-600">缩放进入</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 返回按钮 -->
      <div class="text-center">
        <BaseButton variant="secondary" @click="goBack">
          返回上一页
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseButton from '@/components/BaseButton.vue'
import BaseCard from '@/components/BaseCard.vue'
import BaseModal from '@/components/BaseModal.vue'
import MessageBubble from '@/components/MessageBubble.vue'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'
import EmptyState from '@/components/EmptyState.vue'

const router = useRouter()

// 模态框状态
const showSmallModal = ref(false)
const showMediumModal = ref(false)
const showLargeModal = ref(false)

// 动画状态
const showAnimations = ref(true)

const handleCardClick = () => {
  alert('卡片被点击了！')
}

const handleCreate = () => {
  alert('创建按钮被点击了！')
}

const triggerAnimations = () => {
  showAnimations.value = false
  setTimeout(() => {
    showAnimations.value = true
  }, 100)
}

const goBack = () => {
  router.back()
}
</script>
