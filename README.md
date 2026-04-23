# 智能营养顾问系统

> AI-driven Intelligent Nutrition Advisor System — 基于大语言模型与 RAG 技术的个性化营养健康管理平台

---

## 目录

- [项目概述](#项目概述)
- [核心功能](#核心功能)
- [技术架构](#技术架构)
- [系统目录结构](#系统目录结构)
- [数据库设计](#数据库设计)
- [RAG 知识库系统](#rag-知识库系统)
- [文档解析与向量入库](#文档解析与向量入库)
- [API 接口列表](#api-接口列表)
- [前端页面模块](#前端页面模块)
- [快速开始](#快速开始)
- [配置说明](#配置说明)

---

## 项目概述

智能营养顾问系统是一个**全栈营养健康管理平台**，融合了大语言模型（LLM）、检索增强生成（RAG）、多模态视觉识别和向量数据库技术，为用户提供个性化的营养咨询、食谱推荐、健康档案管理和知识库管理等功能。

### 技术栈总览

| 层级 | 技术选型 |
|------|----------|
| **前端** | Vue 3 + Composition API + Vant 4 (移动端 UI) + Pinia + Vite 5 |
| **后端** | Python 3.10+ / FastAPI + SQLAlchemy ORM + Pydantic |
| **关系数据库** | MySQL 8.0 (用户数据/健康档案/食谱/知识) |
| **向量数据库** | PostgreSQL + pgvector (RAG 知识检索) |
| **LLM** | 豆包 (Doubao seed-2-0-lite) — 营养咨询/食谱推荐/食材替代 |
| **Embedding** | 阿里 DashScope text-embedding-v4 (1024 维) |
| **视觉模型** | 阿里 DashScope qwen-vl-plus — 食材图片识别 |

---

## 核心功能

### 1. 用户认证与权限管理
- 注册/登录（支持用户名/邮箱/手机号三种方式）
- JWT Token 认证，有效期 24 小时
- **管理员系统**：基于 `is_admin` 字段实现角色权限控制
- 管理员拥有知识库管理、用户管理、系统配置等权限

### 2. AI 智能营养咨询
- 对话式营养问答，LLM 驱动的智能回答
- 历史记录持久化存储
- 首页快捷问题标签，一键提问
- 打字动画与消息气泡式交互体验

### 3. 智能食谱推荐（RAG）
- **AI 推荐**：结合用户偏好、已有食材，通过 RAG 检索增强生成个性化食谱
- **季节性推荐**：春/夏/秋/冬四季食材推荐（直接调用 LLM，无需向量检索）
- **食材识别**：多模态视觉模型识别图片中的食材，支持文件上传和 URL 两种方式
- **食材替代**：查询特定食材的替代方案

### 4. 健康档案管理
- **健康档案**：年龄/性别/身高/体重/BMI/活动水平/健康状况
- **饮食偏好**：口味偏好/饮食类型/过敏食物/禁忌食物
- **健康目标**：减肥/增肌/控糖，设定目标体重和每日热量

### 5. 营养知识库
- 传统数据库知识条目（标题/内容/分类/来源）
- **文档解析入库**：上传 PDF/Word/TXT/Markdown 文档，自动分块 → 向量化 → 存入向量数据库
- **知识库搜索**：语义搜索，按分类筛选
- **外部资源链接**：权威营养机构/营养百科/饮食指南/计算工具

### 6. 管理员后台
- **用户管理**：分页列表、角色切换、删除用户
- **行为分析**：日活/周活/月活/留存率（模拟数据）
- **用户反馈**：反馈列表管理
- **知识库管理**：
  - 文档上传（最大 30MB，支持 PDF/Word/TXT/Markdown）
  - 4 种分块方式选择（固定大小/句子/段落/递归）
  - 多种嵌入模型选择
  - **实时进度面板**：4 阶段进度展示（上传→解析→向量化→存储），支持跨页面持久化
  - 解析结果预览（文本块内容/字符数/索引）
- **系统设置**：LLM 参数调节（Temperature/Max Tokens）、Embedding 配置、系统日志

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Vue 3 + Vant 4)               │
│  ┌──────────┐ ┌────────── ┌──────────┐ ──────────┐        │
│  │ 首页     │ │ 营养咨询 │ │ 食谱推荐 │ │ 个人中心 │        │
│  │ Home.vue │ │ Chat.vue │ │ Recipes  │ │ Profile  │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│  ┌──────────┐ ┌────────── ┌──────────┐ ──────────┐        │
│  │ 营养知识 │ │ 健康档案 │ │ 饮食偏好 │ │ 健康目标 │        │
│  │Knowledge │ │ HealthP. │ │ DietPref │ │ H.Goals  │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│  ┌────────── ┌──────────┐ ──────────┐                     │
│  │ 管理员   │ │ 登录     │ │ 注册     │                     │
│  │ Admin    │ │ Login    │ │ Register │                     │
│  └──────────┘ └──────────┘ └──────────┘                     │
│                         ↓ HTTP/Axios                        │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    后端层 (FastAPI)                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │auth     │ │chat     │ │recipes  │ │knowledge│           │
│  │.py      │ │.py      │ │.py      │ │.py      │           │
│  └─────────┘ └───────── └─────────┘ ─────────┘           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │admin    │ │knowledge│ │health_  │ │diet_    │           │
│  │.py      │ │_base.py │ │profile  │ │pref     │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│  ┌────────────┐ ┌────────────┐ ┌────────────              │
│  │llm_service │ │rag_service │ │vector_     │              │
│  │.py         │ │.py         │ │service.py  │              │
│  └────────────┘ └────────────┘ └────────────              │
───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   MySQL 8.0   │  │  PostgreSQL   │  │  Doubao LLM   │
│   (关系数据)  │  │  + pgvector   │  │  + DashScope  │
│               │  │  (向量数据)   │  │  (AI 服务)    │
└───────────────┘  └───────────────┘  └───────────────┘
```

---

## 系统目录结构

```
llmsystem/
├── README.md                          # 项目说明文档
├── backend/                           # 后端服务
│   ├── requirements.txt               # Python 依赖
│   └── app/
│       ├── __init__.py
│       ├── main.py                    # FastAPI 应用入口，CORS, 路由注册
│       ├── config.py                  # 全局配置 (数据库/LLM/Embedding/API Key)
│       ├── database.py                # SQLAlchemy 引擎与 Session 工厂
│       ├── models.py                  # 14 个 ORM 模型 (User/Recipe/Knowledge 等)
│       ├── schemas.py                 # Pydantic 请求/响应模型
│       ├── utils.py                   # JWT 认证、密码加密等工具函数
│       ├── routes/                    # 8 个路由模块
│       │   ├── auth.py               # 注册/登录/获取用户信息
│       │   ├── chat.py               # 对话发送/历史记录
│       │   ├── recipes.py            # AI推荐/食材识别/季节推荐/食材替代
│       │   ├── knowledge.py          # 传统知识库 CRUD/搜索/分类
│       │   ├── knowledge_base.py     # 向量知识库 CRUD/搜索/统计
│       │   ├── health_profile.py     # 健康档案 CRUD
│       │   ├── diet_preferences.py   # 饮食偏好 CRUD
│       │   ├── health_goals.py       # 健康目标 CRUD
│       │   └── admin.py              # 管理员功能 (用户/知识库/设置/日志/文档上传)
│       └── services/                  # 核心业务服务层
│           ├── llm_service.py         # LLM API 调用封装 (聊天/食谱生成/营养建议)
│           ├── rag_service.py         # RAG 检索增强生成 (检索+生成食谱)
│           └── vector_service.py      # 向量数据库操作 (插入/搜索/删除/分页)
│
├── frontend/                          # 前端应用
│   ├── package.json                   # Node 依赖 (Vue 3 / Vant 4 / Pinia)
│   ├── vite.config.js                 # Vite 构建配置 + API 代理
│   ├── index.html
│   └── src/
│       ├── main.js                    # Vue 应用入口
│       ├── App.vue                    # 根组件 (TabBar 导航布局)
│       ├── styles/main.css            # 全局样式 (主题色/动画/组件覆盖)
│       ├── router/index.js            # 路由配置 + 守卫 (认证/管理员)
│       ├── stores/auth.js             # Pinia 认证状态 (用户/Token/isAdmin)
│       ├── api/index.js               # Axios 封装 + 所有 API 调用
│       └── views/
│           ├── Home.vue               # 首页 (Hero/数据卡片/功能网格/贴士)
│           ├── Login.vue              # 登录页 (渐变Hero/图标输入框)
│           ├── Register.vue           # 注册页 (紫色主题/表单验证)
│           ├── Profile.vue            # 个人中心 (用户卡片/菜单分组)
│           ├── Chat.vue               # 营养咨询 (气泡消息/打字动画/快捷问题)
│           ├── Recipes.vue            # 食谱推荐 (AI推荐/食材识别/季节/替代)
│           ├── Knowledge.vue          # 营养知识 (搜索/分类/资源链接/详情弹窗)
│           ├── HealthProfile.vue      # 健康档案
│           ├── DietPreferences.vue    # 饮食偏好
│           ├── HealthGoals.vue        # 健康目标
│           ├── KnowledgeList.vue      # 知识库列表
│           ├── KnowledgeDetail.vue    # 知识详情
│           └── Admin.vue              # 管理后台 (用户/知识库/设置)
│
└── start.ps1                          # Windows 一键启动脚本 (预留)
```

---

## 数据库设计

系统使用 **MySQL 8.0** 存储结构化业务数据，共 **14 张表**：

### 用户与权限
| 表名 | 说明 | 核心字段 |
|------|------|----------|
| `users` | 用户表 | id, username, email, phone, password_hash, avatar, **is_admin**, created_at |

### 健康数据
| 表名 | 说明 | 核心字段 |
|------|------|----------|
| `user_health_profile` | 健康档案 | age, gender, height, weight, bmi, activity_level, health_conditions |
| `user_diet_preferences` | 饮食偏好 | taste_preference, diet_type, allergies, forbidden_foods |
| `user_health_goals` | 健康目标 | goal_type, target_weight, daily_calorie_target |

### 对话与饮食记录
| 表名 | 说明 | 核心字段 |
|------|------|----------|
| `chat_records` | 对话记录 | user_id, question, answer, created_at |
| `diet_records` / `diet_record_items` | 饮食记录 (主从表) | meal_type, total_calories, food_name, quantity, calories |
| `food_recognition_records` | 食材识别记录 | image_url, recognized_food, confidence |

### 食谱与食材 (传统数据)
| 表名 | 说明 | 核心字段 |
|------|------|----------|
| `ingredients` / `ingredient_nutrition` | 食材及营养 (主从表) | name, category, season, calories, protein, fat, carbs |
| `recipes` / `recipe_ingredients` / `recipe_nutrition` | 食谱 (主-多从表) | name, meal_type, difficulty, cook_time |
| `nutrition_knowledge` / `knowledge_embeddings` | 知识条目及向量 (主从表) | title, content, category, source, embedding_vector |

> **关联关系**：User 1→N ChatRecord, User 1→1 HealthProfile, User 1→1 DietPreference, User 1→N HealthGoal, Recipe N→N Ingredient (通过 RecipeIngredient 中间表)

---

## RAG 知识库系统

系统实现了完整的 **Retrieval-Augmented Generation** 流程：

### 知识入库流程
```
上传文档 (PDF/Word/TXT/MD)
        ↓
[文档解析] PyPDF2 / python-docx 提取纯文本
        ↓
[文本分块] 4 种策略可选:
    ① Fixed Chunk    — 固定大小 (chunk_size=500, overlap=50)
    ② Sentence Chunk — 句子级别 (sentences_per_chunk=3)
    ③ Paragraph Chunk— 段落级别 (paragraphs_per_chunk=2)
    ④ Recursive Chunk— 递归分块 (max_chunk_size=512)
        ↓
[向量嵌入] DashScope text-embedding-v4 → 1024 维向量
        ↓
[存储] PostgreSQL + pgvector (knowledge_vectors 表)
```

### 知识检索流程 (RAG)
```
用户请求 → 问题文本
        ↓
[向量化] 用户问题 → embedding (1024 维)
        ↓
[相似度检索] pgvector cosine distance, top_k=5, threshold=0.8
        ↓
[构建 Prompt] system_prompt + 用户上下文 + 检索到的知识片段
        ↓
[LLM 生成] Doubao LLM 生成食谱/营养建议
```

### 核心服务类

**VectorDatabase** (`vector_service.py`)
- `add_vector(content, embedding, content_type, metadata)` — 插入向量记录
- `search(query_embedding, top_k=5, threshold=0.8)` — 余弦相似度搜索
- `get_all_by_type(content_type)` — 按类型获取所有记录
- `get_all(limit, offset)` — 分页获取所有记录
- `count_vectors(content_type)` — 统计指定类型数量
- `delete_vector(vector_id)` — 删除记录

**RAGService** (`rag_service.py`)
- `generate_recipe_with_rag(user_context, meal_type, available_ingredients)` — RAG 食谱推荐
- `add_knowledge(content, content_type, metadata, embedding)` — 添加知识到向量库
- `retrieve_knowledge(query, top_k=5)` — 检索相关知识
- `search_knowledge(query, content_type)` — 语义搜索
- `get_all_knowledge(content_type, page, page_size)` — 分页获取所有知识

**LLMService** (`llm_service.py`)
- `chat_completion(messages, system_prompt, temperature, max_tokens)` — 通用 LLM 对话
- `generate_nutrition_advice(context, question)` — 营养建议生成
- `generate_recipe(context, constraints)` — 食谱生成

---

## 文档解析与向量入库

### 支持的文档格式
| 格式 | 解析库 | 说明 |
|------|--------|------|
| `.pdf` | PyPDF2 3.0.1 | 逐页提取文本内容 |
| `.doc` / `.docx` | python-docx 1.1.0 | 按段落提取文本 |
| `.txt` | 原生读取 | 直接读取 |
| `.md` | 原生读取 | 直接读取 (保留 Markdown 格式) |

### 后台任务处理机制
为避免长耗时操作阻塞 HTTP 请求，采用 **FastAPI BackgroundTasks + 全局任务字典** 方案：

```python
# admin.py
upload_tasks: Dict[str, dict] = {}  # task_id → 任务状态
task_lock = threading.Lock()

@router.post("/document/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    chunk_method: str,
    embedding_model: str,
    content_type: str,
    category: str
):
    task_id = uuid.uuid4().hex
    # 立即返回 task_id，后台异步处理
    background_tasks.add_task(process_document_task, task_id, ...)
    return {"success": True, "task_id": task_id, ...}
```

### 前端进度持久化
用户上传文档后即使离开页面或刷新浏览器，进度也不会丢失：

1. **localStorage 存储**：任务开始时保存 `taskId`/`filename`/`startTime`
2. **自动恢复**：进入知识库 tab 时查询后端状态，恢复进度面板和轮询
3. **页面刷新**：`onMounted` 检测到进行中的任务，自动跳转并恢复
4. **Tab 指示器**：知识库 tab 显示脉冲黄点 `●`，提示有任务运行
5. **4 阶段可视化**：上传文件 → 解析文本 → 生成向量 → 存储知识

---

## API 接口列表

### 认证模块 `/api/v1`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/register` | 用户注册 |
| POST | `/auth/login` | 用户登录 |
| GET | `/auth/me` | 获取当前用户信息 |
| POST | `/auth/logout` | 用户登出 |

### 健康模块 `/api/v1`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/PUT | `/health-profile/` | 健康档案查询/更新 |
| GET/PUT | `/diet-preferences/` | 饮食偏好查询/更新 |
| GET | `/health-goals/` | 健康目标查询 |
| POST | `/health-goals/` | 创建健康目标 |
| PUT | `/health-goals/{id}` | 更新健康目标 |
| DELETE | `/health-goals/{id}` | 删除健康目标 |

### 对话模块 `/api/v1`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/chat/history` | 获取对话历史 (分页) |
| POST | `/chat/` | 发送问题，获取 AI 回答 |

### 食谱模块 `/api/v1`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/recipes/recognize` | 多模态食材识别 (支持 image file 或 image_url) |
| GET | `/recipes/recommend/ai` | AI 智能推荐食谱 (RAG, 可选 season 参数) |
| GET | `/recipes/substitute` | 食材替代方案查询 |

### 知识模块 `/api/v1`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/knowledge/` | 知识列表 (分页/分类) |
| GET | `/knowledge/categories` | 获取所有分类 |
| GET | `/knowledge/{id}` | 知识详情 |
| GET | `/knowledge/search/` | 知识搜索 (关键词) |

### 知识库模块 (向量) `/api/v1`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/knowledge-base/` | 向量知识列表 (分页/类型) |
| POST | `/knowledge-base/` | 添加知识 (文本直接入库) |
| GET | `/knowledge-base/{knowledge_id}` | 知识详情 |
| GET | `/knowledge-base/search/` | 语义搜索 |
| DELETE | `/knowledge-base/{knowledge_id}` | 删除知识 |
| GET | `/knowledge-base/stats/` | 知识统计 (按类型计数) |

### 管理员模块 `/api/v1`
| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/admin/users` | 用户列表 (分页) | 管理员 |
| PUT | `/admin/users/{id}/role` | 切换管理员角色 | 管理员 |
| DELETE | `/admin/users/{id}` | 删除用户 | 管理员 |
| GET | `/admin/stats/activity` | 活跃度统计 | 管理员 |
| GET | `/admin/stats/behavior` | 行为分析 | 管理员 |
| GET | `/admin/feedbacks` | 用户反馈列表 | 管理员 |
| GET/PUT | `/admin/settings/llm` | LLM 参数配置 | 管理员 |
| GET/PUT | `/admin/settings/embedding` | Embedding 配置 | 管理员 |
| GET | `/admin/logs` | 系统日志 | 管理员 |
| GET | `/admin/document/parse-options` | 获取分块/嵌入选项 | 管理员 |
| POST | `/admin/document/upload` | 上传文档 (异步处理) | 管理员 |
| GET | `/admin/document/task/{task_id}` | 查询任务状态 | 管理员 |
| GET | `/admin/document/tasks` | 获取所有任务 | 管理员 |
| GET | `/admin/document/chunks` | 预览分块结果 | 管理员 |

---

## 前端页面模块

| 页面 | 路由 | 功能 | 设计亮点 |
|------|------|------|----------|
| **登录** | `/login` | 用户名/邮箱/手机号登录 | 翡翠绿渐变 Hero 区 + 图标前缀输入框 |
| **注册** | `/register` | 新用户注册 | 紫色主题 Hero 区 + 多字段验证 |
| **首页** | `/home` | 功能入口 + 数据概览 | 时间感知问候 + Hero 横幅 + 彩色功能网格 |
| **营养咨询** | `/chat` | AI 对话 | 气泡消息 + 打字动画 + 快捷问题标签 |
| **食谱推荐** | `/recipes` | AI 推荐 + 食材识别 | 分区卡片 + emoji 季节卡片 + 自定义选择器 |
| **营养知识** | `/knowledge` | 知识浏览 + 外部资源 | 搜索栏 + 胶囊标签 + 向量知识弹窗详情 |
| **个人中心** | `/profile` | 用户信息与设置 | 用户卡片 + 分组菜单 + 退出确认 |
| **健康档案** | `/health-profile` | BMI/身高/体重管理 | — |
| **饮食偏好** | `/diet-preferences` | 口味/过敏/禁忌设置 | — |
| **健康目标** | `/health-goals` | 目标设定与追踪 | — |
| **管理员后台** | `/admin` | 用户/知识库/系统管理 | Tab 导航 + 实时进度面板 + 配置面板 |

### 前端设计系统

**主题配色**
- 主色: `#10b981` 翡翠绿 (健康/营养)
- 辅助色: `#6366f1` 靛蓝紫 (注册/设置)
- 强调色: `#f59e0b` 琥珀色 (提示/任务指示)
- 危险色: `#ef4444` 红色 (错误/删除)
- 背景: `#f0fdf4` 淡绿色调

**动画效果**
- `fadeInUp` — 页面元素入场动画
- `pulse-soft` — 柔和脉冲
- `float` — 浮动动画 (Hero 装饰圆)
- `typingBounce` — 聊天打字三点跳动
- `shimmer` — 进度条流光效果
- `task-pulse` — 任务指示点呼吸动画

---

## 快速开始

### 环境要求

- **Python** 3.8+
- **Node.js** 16+
- **MySQL** 5.7+
- **PostgreSQL** 13+ (with pgvector extension)
- **Conda** (llmenv 环境)

### 后端启动

```bash
# 1. 激活 conda 环境
conda activate llmenv

# 2. 安装依赖
cd backend
pip install -r requirements.txt

# 3. 启动后端服务 (必须从 backend 目录运行)
cd backend
set PYTHONPATH=%CD%        # Windows CMD
# 或
$env:PYTHONPATH = Get-Location  # PowerShell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端启动后可访问：
- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

### 前端启动

```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 启动开发服务器
npm run dev
```

前端访问地址: http://localhost:3000

### 数据库初始化

后端首次启动时会自动创建所有数据表（`Base.metadata.create_all(bind=engine)`），无需手动建表。

---

## 配置说明

所有配置集中在 `backend/app/config.py`，可通过 `.env` 文件覆盖：

```python
# MySQL 数据库 (关系数据)
DB_HOST=8.137.169.98
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Admin0704
DB_NAME=mydb

# PostgreSQL 数据库 (向量数据)
VECTOR_DB_HOST=8.137.169.98
VECTOR_DB_PORT=5432
VECTOR_DB_USER=postgres
VECTOR_DB_PASSWORD=111111
VECTOR_DB_NAME=postgres

# JWT 认证
SECRET_KEY=nutrition-advisor-secret-key-2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 小时

# LLM (豆包 Doubao)
LLM_API_KEY=3cbc368c-e813-4300-890b-804b05504b53
LLM_API_URL=https://ark.cn-beijing.volces.com/api/v3
LLM_MODEL_NAME=doubao-seed-2-0-lite-260215

# Embedding (阿里 DashScope)
DASHSCOPE_API_KEY=sk-ddeca8262dff4c4c89087242035177b6
EMBEDDING_MODEL=text-embedding-v4
EMBEDDING_DIMENSION=1024

# 视觉模型 (阿里 DashScope)
VISION_LLM_API_KEY=sk-ddeca8262dff4c4c89087242035177b6
VISION_LLM_MODEL=qwen-vl-plus
VISION_LLM_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 前端 API 代理配置

`frontend/vite.config.js`:

```javascript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

---

## 技术特色总结

1. **完整的 RAG 系统** — 文档解析 → 多策略分块 → 向量化 → 语义检索 → LLM 增强生成
2. **多模态食材识别** — 单接口支持图片文件上传和 URL 两种输入方式
3. **异步文档处理** — BackgroundTasks + 全局任务字典 + 前端轮询 + localStorage 持久化
4. **角色权限控制** — 管理员系统 + 路由守卫 + 接口级权限校验
5. **现代化前端设计** — 翡翠绿主题 + 卡片式布局 + 渐变装饰 + 流畅动画
6. **双数据源融合** — 传统 MySQL 知识库 + 向量 PostgreSQL 知识库，统一展示

---

*Built with Vue 3 + FastAPI + RAG + LLM*
