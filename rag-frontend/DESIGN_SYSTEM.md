# RAG前端设计系统文档

本文档定义了RAG项目前端的设计规范，包括颜色、字体、间距、组件使用等。

## 颜色系统

### 主题色

```css
/* 主色 - 蓝色系 (Primary) */
primary-50: #eff6ff     /* 极浅 */
primary-100: #dbeafe    /* 很浅 */
primary-500: #3b82f6    /* 标准 */
primary-600: #2563eb    /* 常用 */
primary-700: #1d4ed8    /* 深色 */

/* 成功 - 绿色系 (Success) */
success-500: #22c55e    /* 标准 */
success-600: #16a34a    /* 常用 */

/* 警告 - 琥珀色系 (Warning) */
warning-500: #f59e0b    /* 标准 */
warning-600: #d97706    /* 常用 */

/* 危险 - 红色系 (Danger) */
danger-500: #ef4444     /* 标准 */
danger-600: #dc2626     /* 常用 */

/* 信息 - 青色系 (Info) */
info-500: #06b6d4       /* 标准 */
info-600: #0891b2       /* 常用 */

/* 中性灰 (Gray) */
gray-50: #f8fafc        /* 背景 */
gray-100: #f1f5f9       /* 浅背景 */
gray-200: #e2e8f0       /* 边框 */
gray-300: #cbd5e1       /* 边框深色 */
gray-500: #64748b       /* 次要文本 */
gray-700: #334155       /* 正常文本 */
gray-900: #0f172a       /* 标题文本 */
```

### 使用场景

| 颜色 | 使用场景 |
|------|----------|
| Primary | 主要按钮、链接、选中状态、品牌色 |
| Success | 成功提示、完成状态、积极操作 |
| Warning | 警告提示、需要注意的信息 |
| Danger | 错误提示、删除操作、危险操作 |
| Info | 信息提示、帮助说明 |
| Gray | 文本、边框、背景、禁用状态 |

## 字体系统

### 字体族
```css
font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
```

### 字体大小
```css
text-xs: 0.75rem (12px)      /* 辅助文本、标签 */
text-sm: 0.875rem (14px)     /* 次要文本 */
text-base: 1rem (16px)       /* 正文 */
text-lg: 1.125rem (18px)     /* 小标题 */
text-xl: 1.25rem (20px)      /* 标题 */
text-2xl: 1.5rem (24px)      /* 大标题 */
```

### 字重
```css
font-normal: 400             /* 正文 */
font-medium: 500             /* 强调 */
font-semibold: 600           /* 小标题 */
font-bold: 700               /* 标题 */
```

## 间距系统

### 标准间距
```css
spacing-1: 0.25rem (4px)
spacing-2: 0.5rem (8px)
spacing-3: 0.75rem (12px)
spacing-4: 1rem (16px)       /* 最常用 */
spacing-6: 1.5rem (24px)
spacing-8: 2rem (32px)
spacing-12: 3rem (48px)
```

### 使用建议
- 组件内部间距: spacing-4 (16px)
- 组件之间间距: spacing-6 (24px)
- 区块之间间距: spacing-8 (32px)

## 圆角系统

```css
rounded: 0.25rem (4px)          /* 小元素 */
rounded-lg: 0.5rem (8px)        /* 按钮、输入框 */
rounded-xl: 0.75rem (12px)      /* 卡片 */
rounded-2xl: 1rem (16px)        /* 消息气泡 */
rounded-full: 9999px            /* 圆形头像、徽章 */
```

## 阴影系统

```css
shadow-sm: 小阴影              /* 按钮、输入框 */
shadow: 标准阴影               /* 默认 */
shadow-soft: 柔和阴影          /* 卡片 */
shadow-soft-lg: 大柔和阴影     /* 模态框、悬停 */
```

## 动画系统

### 过渡时长
```css
duration-200: 200ms            /* 快速交互 */
duration-300: 300ms            /* 标准过渡 */
duration-400: 400ms            /* 慢速过渡 */
```

### 内置动画
```css
animate-fade-in: 淡入
animate-fade-in-up: 向上淡入
animate-slide-in-right: 从右滑入
animate-slide-in-left: 从左滑入
animate-scale-in: 缩放进入
animate-pulse-soft: 柔和脉冲
```

## 组件使用指南

### 按钮 (BaseButton)

**引入:**
```vue
import BaseButton from '@/components/BaseButton.vue'
```

**基本用法:**
```vue
<BaseButton variant="primary" @click="handleClick">
  确认
</BaseButton>
```

**变体:**
- `primary`: 主要按钮 (蓝色)
- `secondary`: 次要按钮 (灰色)
- `success`: 成功按钮 (绿色)
- `danger`: 危险按钮 (红色)
- `ghost`: 幽灵按钮 (透明)

**大小:**
- `sm`: 小按钮
- `md`: 中等按钮 (默认)
- `lg`: 大按钮

**Props:**
- `variant`: 按钮变体
- `size`: 按钮大小
- `disabled`: 是否禁用
- `loading`: 是否加载中
- `block`: 是否全宽

**示例:**
```vue
<!-- 主要按钮 -->
<BaseButton variant="primary">保存</BaseButton>

<!-- 加载中的按钮 -->
<BaseButton variant="primary" :loading="isSubmitting">提交中...</BaseButton>

<!-- 带图标的按钮 -->
<BaseButton variant="danger">
  <template #icon>
    <svg class="w-4 h-4">...</svg>
  </template>
  删除
</BaseButton>

<!-- 全宽按钮 -->
<BaseButton variant="primary" block>立即注册</BaseButton>
```

---

### 卡片 (BaseCard)

**引入:**
```vue
import BaseCard from '@/components/BaseCard.vue'
```

**基本用法:**
```vue
<BaseCard title="卡片标题" :hover="true">
  <p>卡片内容</p>
</BaseCard>
```

**Props:**
- `title`: 卡片标题
- `hover`: 是否有悬停效果
- `padding`: 是否有内边距
- `clickable`: 是否可点击

**示例:**
```vue
<!-- 基本卡片 -->
<BaseCard title="统计信息">
  <p>今日访问: 1,234</p>
</BaseCard>

<!-- 可悬停可点击的卡片 -->
<BaseCard :hover="true" :clickable="true" @click="handleCardClick">
  <div class="flex items-center">
    <img src="..." class="w-16 h-16">
    <div>
      <h4>文档名称</h4>
      <p class="text-sm text-gray-500">上传时间: 2024-01-01</p>
    </div>
  </div>
</BaseCard>

<!-- 自定义头部和底部 -->
<BaseCard>
  <template #header>
    <div class="flex items-center justify-between">
      <h3>自定义标题</h3>
      <button>操作</button>
    </div>
  </template>

  <p>卡片内容</p>

  <template #footer>
    <div class="flex justify-end space-x-2">
      <BaseButton variant="secondary">取消</BaseButton>
      <BaseButton variant="primary">确认</BaseButton>
    </div>
  </template>
</BaseCard>
```

---

### 模态框 (BaseModal)

**引入:**
```vue
import BaseModal from '@/components/BaseModal.vue'
```

**基本用法:**
```vue
<BaseModal v-model="showDialog" title="对话框标题">
  <p>对话框内容</p>
  <template #footer>
    <BaseButton variant="secondary" @click="showDialog = false">取消</BaseButton>
    <BaseButton variant="primary" @click="handleConfirm">确认</BaseButton>
  </template>
</BaseModal>
```

**Props:**
- `modelValue (v-model)`: 是否显示
- `title`: 模态框标题
- `size`: 大小 (sm/md/lg/xl/2xl)
- `showClose`: 是否显示关闭按钮
- `closeOnClickOutside`: 点击背景是否关闭
- `contentPadding`: 内容区是否有内边距

**示例:**
```vue
<script setup>
import { ref } from 'vue'

const showCreateDialog = ref(false)
const formData = ref({ name: '', description: '' })

const handleCreate = () => {
  // 处理创建逻辑
  showCreateDialog.value = false
}
</script>

<template>
  <!-- 触发按钮 -->
  <BaseButton @click="showCreateDialog = true">创建</BaseButton>

  <!-- 模态框 -->
  <BaseModal v-model="showCreateDialog" title="创建知识库" size="md">
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">名称</label>
        <input v-model="formData.name" class="input" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">描述</label>
        <textarea v-model="formData.description" class="input" rows="3"></textarea>
      </div>
    </div>

    <template #footer>
      <BaseButton variant="secondary" @click="showCreateDialog = false">取消</BaseButton>
      <BaseButton variant="primary" @click="handleCreate">创建</BaseButton>
    </template>
  </BaseModal>
</template>
```

---

### 消息气泡 (MessageBubble)

**引入:**
```vue
import MessageBubble from '@/components/MessageBubble.vue'
```

**基本用法:**
```vue
<MessageBubble
  role="user"
  content="用户发送的消息"
  sender-name="张三"
  :timestamp="Date.now()"
  :show-avatar="true"
/>
```

**Props:**
- `role`: 消息角色 (user/assistant)
- `content`: 消息内容
- `senderName`: 发送者名称
- `timestamp`: 时间戳
- `status`: 消息状态 (sending/sent/error)
- `showAvatar`: 是否显示头像
- `showHeader`: 是否显示消息头部
- `showStatus`: 是否显示状态

**示例:**
```vue
<!-- 用户消息 -->
<MessageBubble
  role="user"
  content="你好,请帮我分析一下这份文档"
  sender-name="用户"
  :timestamp="message.createdAt"
  :show-avatar="true"
  :show-header="true"
/>

<!-- AI消息 - 使用slot自定义渲染 -->
<MessageBubble
  role="assistant"
  :show-avatar="true"
>
  <div v-html="renderedMarkdown"></div>
</MessageBubble>

<!-- 发送中的消息 -->
<MessageBubble
  role="user"
  content="正在发送的消息..."
  status="sending"
  :show-status="true"
/>
```

---

### 加载骨架屏 (LoadingSkeleton)

**引入:**
```vue
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'
```

**基本用法:**
```vue
<LoadingSkeleton type="card" :rows="3" />
```

**类型:**
- `text`: 文本骨架屏
- `card`: 卡片骨架屏
- `list`: 列表骨架屏
- `custom`: 自定义骨架屏

**示例:**
```vue
<!-- 加载中显示骨架屏,加载完成显示内容 -->
<LoadingSkeleton v-if="loading" type="list" :rows="5" :avatar="true" />
<div v-else>
  <div v-for="item in items" :key="item.id">
    <!-- 实际内容 -->
  </div>
</div>
```

---

### 空状态 (EmptyState)

**引入:**
```vue
import EmptyState from '@/components/EmptyState.vue'
```

**基本用法:**
```vue
<EmptyState
  title="暂无对话"
  description="开始一个新的对话吧"
>
  <template #action>
    <BaseButton variant="primary" @click="startChat">开始对话</BaseButton>
  </template>
</EmptyState>
```

**Props:**
- `title`: 标题
- `description`: 描述
- `iconType`: 图标类型

**示例:**
```vue
<!-- 无数据时显示 -->
<div v-if="conversations.length === 0">
  <EmptyState
    title="还没有对话历史"
    description="与AI开始一段精彩的对话吧"
  >
    <template #action>
      <BaseButton variant="primary" @click="goToChat">
        开始对话
      </BaseButton>
    </template>
  </EmptyState>
</div>
```

---

## 全局样式类

### 按钮类
```css
.btn                          /* 基础按钮 */
.btn-primary                  /* 主要按钮 */
.btn-secondary                /* 次要按钮 */
.btn-success                  /* 成功按钮 */
.btn-danger                   /* 危险按钮 */
.btn-ghost                    /* 幽灵按钮 */
.btn-sm                       /* 小按钮 */
.btn-lg                       /* 大按钮 */
```

### 卡片类
```css
.card                         /* 基础卡片 */
.card-hover                   /* 可悬停卡片 */
.card-padding                 /* 带内边距 */
```

### 输入框类
```css
.input                        /* 基础输入框 */
.input-error                  /* 错误状态 */
```

### 徽章类
```css
.badge                        /* 基础徽章 */
.badge-primary                /* 主色徽章 */
.badge-success                /* 成功徽章 */
.badge-warning                /* 警告徽章 */
.badge-danger                 /* 危险徽章 */
```

### 实用工具类
```css
.text-ellipsis-2              /* 两行省略 */
.text-ellipsis-3              /* 三行省略 */
.glass                        /* 玻璃态效果 */
.gradient-text                /* 渐变文本 */
.gradient-primary             /* 主色渐变背景 */
```

---

## 最佳实践

### 1. 颜色使用
- ✅ 使用语义化的颜色类,如 `text-primary-600`, `bg-success-100`
- ❌ 避免硬编码颜色值,如 `style="color: #3b82f6"`
- ✅ 统一使用设计系统中定义的颜色

### 2. 间距使用
- ✅ 使用 Tailwind 的间距类,如 `p-4`, `mb-6`
- ❌ 避免使用任意值,如 `p-[13px]`
- ✅ 保持间距的一致性

### 3. 组件复用
- ✅ 优先使用设计系统中的组件
- ✅ 需要新组件时,先考虑是否可以扩展现有组件
- ❌ 避免在页面中重复编写相同的UI逻辑

### 4. 动画使用
- ✅ 为交互添加适当的动画反馈
- ❌ 避免过度使用动画,影响性能
- ✅ 使用设计系统中定义的动画

### 5. 响应式设计
- ✅ 使用 Tailwind 的响应式前缀,如 `md:`, `lg:`
- ✅ 移动端优先,然后适配桌面端
- ✅ 测试不同屏幕尺寸下的表现

---

## 更新日志

### 2024-01-XX
- 初始化设计系统
- 创建基础组件库
- 定义颜色、字体、间距规范
