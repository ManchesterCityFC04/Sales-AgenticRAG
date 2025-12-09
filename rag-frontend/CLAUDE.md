# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 Vue 3 + Vite 的 RAG 系统前端应用，提供智能对话、知识库管理和文档上传功能。使用 Element Plus 作为 UI 组件库，Pinia 进行状态管理，Tailwind CSS 处理样式。

## 常用开发命令

```bash
# 依赖管理
npm install                    # 安装依赖

# 开发服务器
npm run dev                    # 启动开发服务器（端口5173）

# 构建和预览
npm run build                  # 构建生产版本
npm run preview                # 预览生产构建

# 服务地址
# - 前端开发服务器: http://localhost:5173
# - 后端API代理: http://localhost:8000（通过Vite代理）
```

## 项目架构

### 核心目录结构
- `src/main.js` - 应用入口，注册路由、状态管理和UI组件库
- `src/App.vue` - 根组件
- `src/router/index.js` - 路由配置，包含路由守卫
- `src/views/` - 页面组件（5个）
  - `Chat.vue` - 聊天界面（主要功能页面）
  - `Login.vue` - 登录注册页面
  - `History.vue` - 对话历史记录
  - `DocumentLibrary.vue` - 文档库管理
  - `KnowledgeGraph.vue` - 知识图谱可视化（基于ECharts）
- `src/stores/` - Pinia状态管理
  - `auth.js` - 认证状态管理
  - `chat.js` - 聊天状态管理
- `src/api/` - API接口模块
  - `config.js` - HTTP客户端和请求配置
  - `auth.js` - 认证接口
  - `chat.js` - 聊天接口
  - `knowledge.js` - 知识库接口
- `src/utils/` - 工具函数
- `src/components/` - 可复用组件

### 技术栈
- **框架**: Vue 3 (Composition API + script setup)
- **构建工具**: Vite 7.x
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **样式**: Tailwind CSS + Tailwind Typography
- **Markdown渲染**: markdown-it
- **图表库**: ECharts 6.0（用于知识图谱可视化）
- **HTTP客户端**: 自定义 HttpClient（基于fetch）

### API代理配置

⚠️ **重要**: Vite开发服务器需要配置完整的API代理路径，否则会出现404错误。

**当前配置问题**: 默认的`vite.config.js`可能仅配置了`/api`路径，需要添加其他后端路径。

**完整代理配置** (vite.config.js):
```javascript
export default defineConfig({
  server: {
    proxy: {
      // 认证接口
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      // 聊天和对话接口
      '/llm': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      // 知识库管理接口
      '/knowledge': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      // 爬虫接口
      '/crawl': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      // 通用API接口（如需要）
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

**配置说明**:
- 所有代理请求转发到 `http://localhost:8000`（后端FastAPI服务）
- `changeOrigin: true` - 修改请求头中的Origin字段，避免CORS问题
- `secure: false` - 允许HTTPS转发到HTTP（开发环境）
- `/api`路径可选，根据实际后端路由决定是否需要

### 认证系统

完整的JWT认证流程：
- Token存储在localStorage的`auth_token`字段
- 用户信息存储在localStorage的`user_info`字段
- HTTP客户端自动在请求头添加`Authorization: Bearer <token>`
- 路由守卫（router/index.js:49-67）自动保护需要认证的路由
- 认证失败自动重定向到登录页

### 聊天功能

支持两种聊天模式：
1. **标准模式**：通过`/llm/chat`接口发送请求，等待完整响应
2. **流式模式**：通过`/llm/chat/stream`接口使用SSE（Server-Sent Events）获取实时响应

流式聊天实现（api/chat.js:34-108）：
- 使用fetch ReadableStream API读取流式数据
- 支持`data: `格式的SSE消息解析
- 提供`StreamChatManager`辅助类管理流式聊天状态

### 状态管理模式

使用Pinia Composition API风格：
- `useAuthStore` - 管理登录、注册、登出和认证状态初始化
- `useChatStore` - 管理聊天消息、对话历史和会话列表

状态持久化策略：
- Token和用户信息存储在localStorage
- 应用启动时自动调用`authStore.initAuth()`恢复认证状态（main.js:17-18）

## 开发注意事项

### HTTP客户端架构

自定义`HttpClient`类（api/config.js:23-173）提供：
- 统一的请求拦截和错误处理
- 自动token管理和请求头注入
- 30秒请求超时控制
- 401错误自动清除token
- 支持FormData和JSON格式请求体

### 路由配置

所有需要认证的路由必须设置`meta: { requiresAuth: true }`（router/index.js）：
```javascript
{
  path: '/chat',
  name: 'chat',
  component: Chat,
  meta: { requiresAuth: true }
}
```

路由守卫会自动检查`authStore.isAuthenticated`状态

### 组件开发规范

- 使用 Vue 3 `<script setup>` 语法
- Composition API 进行逻辑组织
- 组件样式优先使用 Tailwind CSS utility classes
- 复杂UI组件使用 Element Plus

### 知识图谱可视化

**页面组件**: `src/views/KnowledgeGraph.vue`

**功能说明**:
- 展示知识库的实体和关系图谱
- 使用ECharts力导向图布局
- 支持交互式节点拖拽和缩放
- 数据来源: `/api/visual_graph/{collection_id}` API

**路由配置**:
```javascript
{
  path: '/knowledge-graph/:collection_id',
  name: 'knowledge-graph',
  component: KnowledgeGraph,
  meta: { requiresAuth: true }
}
```

**使用场景**:
- 用户在知识库管理页面点击"查看图谱"按钮
- 通过collection_id参数加载对应知识库的图谱数据
- 可视化知识库中的实体关系和结构

**技术实现**:
- ECharts 6.0 力导向图（force layout）
- 节点大小根据关系数量动态调整
- 边的粗细根据关系强度调整
- 支持图例显示不同类型的实体

### 与后端API对接

API接口文件包含后端对应路由的注释引用，例如：
```javascript
/**
 * 认证相关API接口
 * 对接后端 /workspace/rag-zxj/rag-demo/backend/api/auth.py
 */
```

这有助于快速定位后端对应的实现文件

## 常见开发问题

### 1. API请求404错误

**现象**: 前端调用API时返回404 Not Found

**原因**: Vite代理配置不完整，缺少某些后端路径的代理配置

**解决方案**:
1. 检查`vite.config.js`中的proxy配置
2. 确保包含所有后端路径: `/auth`, `/llm`, `/knowledge`, `/crawl`
3. 参考上方"API代理配置"章节的完整配置
4. 修改配置后重启开发服务器: `npm run dev`

### 2. CORS跨域错误

**现象**: 控制台出现CORS相关错误

**原因**:
- Vite代理未正确配置
- 后端服务未启动或端口不是8000

**解决方案**:
1. 确认后端服务运行在`http://localhost:8000`
2. 检查Vite代理配置中的`changeOrigin: true`
3. 确保后端FastAPI服务已配置CORS中间件

### 3. Token过期跳转登录

**现象**: 操作过程中突然跳转到登录页

**原因**: JWT access token过期（默认24小时）

**说明**: 这是正常行为，安全机制设计

**解决方案**:
- 重新登录即可
- 未来可实现refresh token自动续期机制

### 4. 依赖安装失败

**现象**: `npm install`报错或依赖冲突

**解决方案**:
```bash
# 清理缓存和node_modules
rm -rf node_modules package-lock.json
# 重新安装
npm install
# 或使用npm的清理安装
npm ci
```

### 5. 开发服务器启动失败

**检查清单**:
- Node.js版本是否 >= 16
- 端口5173是否被占用
- 是否在正确的目录下（rag-frontend/）
- package.json和vite.config.js是否存在

### 6. 流式聊天显示异常

**原因**: SSE消息格式解析错误

**检查**:
- 后端是否正确发送`data: `前缀的SSE消息
- 网络连接是否稳定
- 浏览器是否支持ReadableStream API

### 7. ECharts图表不显示

**原因**:
- ECharts组件未正确初始化
- 容器高度为0

**解决方案**:
- 确保容器元素有明确的高度
- 检查ECharts初始化时机（数据加载后）
- 窗口大小改变时调用`chart.resize()`
