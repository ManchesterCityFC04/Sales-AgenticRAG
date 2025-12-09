# Sales-AgenticRAG - 智能销售助手系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)
![Vue](https://img.shields.io/badge/Vue-3.x-4FC08D.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**基于LangGraph的智能RAG销售助手，支持多知识库、向量检索、图检索和销售场景优化**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [架构设计](#-架构设计) • [销售场景](#-销售场景应用)

</div>

---

## 📖 项目简介

Sales-AgenticRAG 是一个面向销售场景的智能问答系统，结合了**检索增强生成（RAG）**、**知识图谱**和**LangGraph智能体**技术。系统能够理解客户意图、分析需求、推荐产品，并生成专业的销售话术，帮助销售团队提升转化率。

### 核心亮点

- 🎯 **销售场景优化**：内置销售意图识别、客户需求分析、产品推荐等销售专用功能
- 🔍 **多模式检索**：支持向量检索、图检索和混合检索，自动选择最优检索策略
- 📚 **多知识库管理**：支持创建多个独立的知识库，实现数据隔离
- 🤖 **智能体工作流**：基于LangGraph构建的8节点智能决策流程
- 💬 **流式对话**：支持实时流式响应，提供流畅的对话体验
- 🎨 **现代化UI**：Vue 3 + Tailwind CSS构建的美观前端界面

---

## ✨ 功能特性

### 销售场景功能

- **销售意图识别**：自动识别产品咨询、价格谈判、竞品对比、异议处理等6种销售意图
- **客户需求分析**：分析客户预算、使用场景、关注点，判断决策阶段
- **智能产品推荐**：基于客户需求和知识库内容，推荐最匹配的产品配置
- **销售话术生成**：使用SPIN提问法和FAB法则，生成个性化销售话术
- **竞品对比分析**：支持竞品信息爬取和对比分析

### 技术功能

- **智能检索判断**：LLM自动判断是否需要检索，避免不必要的检索开销
- **子问题扩展**：将复杂问题分解为多个子问题，提高检索精度
- **检索类型选择**：智能选择向量检索或图检索，优化检索效果
- **知识图谱可视化**：可视化展示知识库中的实体关系
- **文档管理**：支持PDF、Word、网页等多种文档格式的上传和处理
- **对话历史**：保存完整的对话历史，支持会话管理

---

## 🚀 快速开始

### 环境要求

- Python >= 3.12
- Node.js >= 18
- Docker & Docker Compose（用于Milvus）
- MySQL 8.0+
- PostgreSQL 12+（用于LangGraph状态存储）

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/Sales-AgenticRAG.git
cd Sales-AgenticRAG
```

### 2. 后端配置

```bash
cd rag-backend

# 安装依赖（使用uv）
uv sync

# 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 文件，配置以下必需项：
# - DASHSCOPE_API_KEY（阿里云DashScope API密钥）
# - DB_URL（MySQL连接串）
# - POSTGRES_*（PostgreSQL配置）

# 初始化数据库
python backend/init_db.py

# 启动Milvus向量数据库
cd backend/rag/storage
docker-compose up -d

# 返回项目根目录，启动后端服务
cd ../../..
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 3. 前端配置

```bash
cd rag-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

### 4. 访问系统

打开浏览器访问 `http://localhost:5173`，使用以下默认账号登录：
- 邮箱：`demo@example.com`
- 密码：`demo123456`

---

## 🏗️ 架构设计

### 系统架构图

```
┌─────────────────┐
│   Vue 3 前端    │
│  (Tailwind CSS) │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  FastAPI 后端   │
│  (RESTful API)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ LangGraph│ │ 知识库管理 │
│ 智能体   │ │ 文档处理  │
└────┬───┘ └────┬─────┘
     │          │
     │    ┌─────┴─────┐
     │    │           │
     ▼    ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Milvus │ │LightRAG│ │ MySQL  │
│ 向量库  │ │ 图数据库 │ │业务数据库│
└────────┘ └────────┘ └────────┘
```

### LangGraph工作流

系统使用LangGraph构建了8节点的智能决策流程：

```
START
  │
  ▼
[判断是否需要检索]
  │
  ├─ 否 → [直接回答] → END
  │
  └─ 是 → [扩展子问题]
           │
           ▼
      [判断检索类型]
           │
           ├─ 向量检索 → [向量数据库检索]
           │                │
           └─ 图检索 → [图数据库检索]
                          │
                          ▼
                    [生成答案] → END
```

### 核心模块

#### 后端模块

- **`backend/api/`** - API路由层
  - `chat.py` - 聊天接口（流式/非流式）
  - `rag.py` - RAG检索接口
  - `knowledge_library.py` - 知识库管理
  - `visual_graph.py` - 知识图谱可视化
  - `auth.py` - 用户认证
  - `crawl.py` - 网页爬虫

- **`backend/agent/`** - LangGraph智能体
  - `graph/raggraph.py` - RAG图主实现
  - `graph/raggraph_node.py` - 图节点实现
  - `graph/sales_extension.py` - 销售场景扩展
  - `prompts/raggraph_prompt.py` - 提示词管理
  - `states/raggraph_state.py` - 状态定义

- **`backend/rag/`** - RAG核心功能
  - `storage/milvus_storage.py` - Milvus向量存储
  - `storage/lightrag_storage.py` - LightRAG图存储
  - `chunks/` - 文档切块处理

#### 前端模块

- **`src/views/`** - 页面视图
  - `Chat.vue` - 聊天界面
  - `DocumentLibrary.vue` - 文档库管理
  - `KnowledgeGraph.vue` - 知识图谱可视化
  - `History.vue` - 对话历史

- **`src/components/`** - 组件
  - `SalesModePanel.vue` - 销售模式面板
  - `MessageBubble.vue` - 消息气泡
  - `BaseModal.vue` - 基础模态框

---

## 💼 销售场景应用

### 使用场景

#### 1. 产品咨询

**客户提问**：`"这款车的续航里程是多少？"`

**系统处理流程**：
1. 意图识别 → `product_inquiry`
2. 需求分析 → 关注点：续航
3. 检索知识库 → 获取产品参数信息
4. 生成销售话术 → 突出续航优势，结合使用场景

**示例回答**：
> 🚗 **产品介绍**
> 
> 根据您关注的续航，我为您推荐：
> 
> 这款车搭载了最新的电池技术，综合续航里程达到**650公里**，在同级别车型中表现优异。无论是日常通勤还是周末出游，都能满足您的需求。而且支持快充，30分钟即可充电至80%，让您出行无忧。
> 
> ---
> 
> 💡 如果您还有其他问题，欢迎随时咨询！

#### 2. 价格谈判

**客户提问**：`"这个配置多少钱？有没有优惠？"`

**系统处理流程**：
1. 意图识别 → `price_negotiation`
2. 检索价格信息 → 获取官方报价和优惠政策
3. 生成销售话术 → 强调价值，提供优惠方案

#### 3. 竞品对比

**客户提问**：`"和XX品牌相比，你们的优势在哪里？"`

**系统处理流程**：
1. 意图识别 → `competitor_comparison`
2. 爬取竞品信息（可选）
3. 检索产品优势信息
4. 生成对比分析话术

#### 4. 异议处理

**客户提问**：`"我担心电池安全性"`

**系统处理流程**：
1. 意图识别 → `objection_handling`
2. 检索安全相关信息
3. 生成异议处理话术 → 消除疑虑，建立信任

### 销售模式配置

在聊天界面启用销售模式后，系统会自动：

1. **意图识别**：分析客户问题，识别销售意图类型
2. **需求画像**：提取预算、场景、关注点等信息
3. **智能推荐**：基于需求匹配最合适的产品
4. **话术生成**：使用销售技巧生成专业话术

### 销售话术特点

- ✅ 使用**SPIN提问法**（Situation, Problem, Implication, Need-payoff）
- ✅ 应用**FAB法则**（Feature, Advantage, Benefit）
- ✅ 场景化描述，增强代入感
- ✅ 突出产品优势，弱化劣势
- ✅ 引导客户决策，促进成交

---

## 📚 知识库管理

### 创建知识库

1. 登录系统后，进入"文档库"页面
2. 点击"新建知识库"
3. 填写知识库名称和描述
4. 上传产品文档（PDF、Word等格式）

### 文档处理流程

1. **文档上传** → 前端上传到阿里云OSS
2. **文档解析** → 使用MinerU OCR提取文本和图片
3. **文档切块** → 按语义切分为chunks
4. **向量化** → 使用text-embedding-v4生成向量
5. **存储** → 存入Milvus向量库和LightRAG图库
6. **索引完成** → 可用于检索

### 知识图谱构建

系统使用LightRAG自动构建知识图谱：
- 实体抽取：产品、配置、参数等
- 关系抽取：产品-配置、配置-参数等关系
- 图存储：存储在LightRAG workspace中

---

## 🔧 配置说明

### 环境变量配置

#### 必需配置

```bash
# 大模型API密钥（必需）
DASHSCOPE_API_KEY=your_dashscope_api_key

# MySQL数据库（必需）
DB_URL=mysql+pymysql://user:password@localhost:3306/rag_db

# PostgreSQL配置（必需，用于LangGraph状态存储）
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=rag_checkpoint
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

#### 可选配置

```bash
# Milvus配置
MILVUS_URI=http://localhost:19530
MILVUS_DB_NAME=default

# LightRAG配置
LIGHTRAG_WORKSPACE=./backend/rag/storage/lightrag_storage

# 阿里云OSS配置（文档存储）
OSS_ACCESS_KEY_ID=your_access_key
OSS_ACCESS_KEY_SECRET=your_secret_key
OSS_REGION=cn-shanghai
OSS_BUCKET_NAME=your_bucket_name

# JWT认证配置
JWT_SECRET_KEY=your_secret_key
JWT_ACCESS_TOKEN_EXPIRES=86400
```

完整配置说明请参考 `rag-backend/backend/.env.example`

---

## 🧪 测试

### 运行测试

```bash
cd rag-backend
uv run pytest backend/tests/ -v
```

### 主要测试文件

- `test_raggraph_simple.py` - RAG图基本功能测试
- `test_raggraph_vector.py` - 向量检索测试
- `test_raggraph_lightrag.py` - 图检索测试
- `test_chunk.py` - 文档切块测试
- `test_crawl.py` - 爬虫功能测试

---

## 📊 技术栈

### 后端技术

- **框架**：FastAPI 0.116+
- **智能体**：LangGraph 0.6.6
- **LLM**：通义千问（qwen3-max-preview）
- **向量模型**：阿里云 text-embedding-v4
- **向量数据库**：Milvus 2.6.0
- **图数据库**：LightRAG
- **业务数据库**：MySQL 8.0+
- **状态存储**：PostgreSQL 12+
- **文档处理**：MinerU OCR、PyPDF2、python-docx
- **爬虫**：crawl4ai

### 前端技术

- **框架**：Vue 3 + Vite
- **UI库**：Tailwind CSS
- **图表**：ECharts
- **图谱可视化**：Cytoscape.js
- **状态管理**：Pinia

---

## 📝 API文档

启动后端服务后，访问以下地址查看API文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 主要API端点

- `POST /api/chat/stream` - 流式聊天接口
- `POST /api/chat` - 非流式聊天接口
- `POST /api/rag/query` - RAG检索接口
- `GET /api/knowledge-libraries` - 获取知识库列表
- `POST /api/knowledge-libraries` - 创建知识库
- `POST /api/knowledge-libraries/{id}/documents` - 上传文档
- `GET /api/visual-graph/{collection_id}` - 获取知识图谱数据

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - 智能体工作流框架
- [LangChain](https://github.com/langchain-ai/langchain) - LLM应用开发框架
- [LightRAG](https://github.com/HKUDS/LightRAG) - 轻量级RAG图数据库
- [Milvus](https://milvus.io/) - 向量数据库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架

---

## 📮 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue: [GitHub Issues](https://github.com/yourusername/Sales-AgenticRAG/issues)
- 邮箱: your-email@example.com

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！⭐**

Made with ❤️ by Sales-AgenticRAG Team

</div>

