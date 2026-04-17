# LLM Graph Builder Backend - 航空航天机械故障诊断系统

## 项目概述

LLM Graph Builder Backend 是一个基于 FastAPI 构建的高性能后端服务，专门为航空航天机械故障诊断与健康管理（PHM）领域设计。该服务能够将非结构化的技术文档、维修手册、故障报告等数据，通过大型语言模型（LLM）转换为结构化的知识图谱，存储在 Neo4j 图数据库中，支持智能查询、可视化和诊断分析。

## 🎯 设计理念

本后端服务遵循以下设计原则：
- **高并发处理**：使用 FastAPI 和 Uvicorn 实现 ASGI 架构，支持高并发请求
- **模块化设计**：各功能模块解耦，便于维护和扩展
- **异步非阻塞**：大量使用 async/await 提高处理效率
- **容错设计**：完善的异常处理和日志记录机制
- **可扩展性**：支持多种LLM模型和数据源的集成

## 🏗️ 架构概览

### 系统架构图
```
┌─────────────────────────────────────────────────────────────────────────┐
│                          API 网关层                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│  │   FastAPI      │  │    路由管理     │  │   中间件       │        │
│  │     路由       │  │    (CORS)      │  │   (GZip/Session)│        │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          业务逻辑层                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│  │   文档处理     │  │   图谱生成     │  │   智能对话     │        │
│  │   模块         │  │   引擎         │  │   系统         │        │
│  │                │  │                │  │                │        │
│  │ • 文件上传      │  │ • Schema定义   │  │ • 多模式查询   │        │
│  │ • 分块处理      │  │ • 实体提取     │  │ • 上下文管理   │        │
│  │ • 格式转换      │  │ • 关系构建     │  │ • 响应生成     │        │
│  │                │  │ • 优化处理     │  │                │        │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          服务层                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│  │   LLM 接口     │  │   数据库访问   │  │   文件存储     │        │
│  │   管理         │  │   层           │  │   管理         │        │
│  │                │  │                │  │                │        │
│  │ • GLM-4/4.6v   │  │ • Neo4j 连接   │  │ • MinIO 对象   │        │
│  │ • DeepSeek     │  │ • 查询优化     │  │ • 本地文件     │        │
│  │ • Qwen         │  │ • 事务管理     │  │ • 缓存管理     │        │
│  │ • Ollama       │  │                │  │                │        │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          数据层                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│  │   知识图谱     │  │   向量存储     │  │   日志系统     │        │
│  │   (Neo4j)      │  │   (FAISS)      │  │   (文件)       │        │
│  │                │  │                │  │                │        │
│  │ • 节点管理     │  │ • 文档嵌入     │  │ • 操作日志     │        │
│  │ • 关系管理     │  │ • 相似度检索   │  │ • 错误日志     │        │
│  │ • 索引优化     │  │ • 向量更新     │  │ • 性能监控     │        │
│  │ • Schema 验证  │  │                │  │                │        │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
```

### 核心模块详解

#### 1. LLM 接口层 (`src/llm.py`)
```python
class LLMManager:
    """LLM 模型统一管理"""
    def __init__(self):
        self.models = {
            "GLM": ChatZhipuAI,
            "DeepSeek": ChatDeepSeekAI,
            "Qwen": ChatQianwenAI,
            "Ollama": ChatOllama
        }
    
    def get_llm(self, model_name: str, **kwargs):
        """根据模型名称获取LLM实例"""
        if model_name in self.models:
            return self.models[model_name](**kwargs)
        raise ValueError(f"Unsupported model: {model_name}")
```

#### 2. 图谱处理层 (`src/main.py`)
```python
def generate_graph_documents(graph, model, documents, allowed_nodes, allowed_relationships):
    """生成知识图谱文档"""
    # 1. 使用 LLM 提取实体和关系
    graph_documents = []
    
    for doc in documents:
        # 提取结构化数据
        entities = extract_entities(doc.page_content, model, allowed_nodes)
        relationships = extract_relationships(doc.page_content, model, allowed_relationships)
        
        # 创建 GraphDocument
        graph_doc = create_graph_document(
            nodes=entities,
            relationships=relationships,
            source=doc.metadata
        )
        graph_documents.append(graph_doc)
    
    return graph_documents
```

#### 3. 存储管理层 (`src/graphDB_dataAccess.py`)
```python
class graphDBdataAccess:
    """Neo4j 数据库访问层"""
    def __init__(self, graph: Neo4jGraph):
        self.graph = graph
        
    def create_source_node(self, source_node: sourceNode):
        """创建源节点"""
        query = """
        CREATE (s:Source {
            file_name: $file_name,
            file_source: $file_source,
            file_type: $file_type,
            model: $model,
            created_at: $created_at,
            file_size: $file_size
        })
        """
        self.graph.query(query, parameters=source_node.__dict__)
        
    def create_entities_from_chunks(self, chunks: List[chunk]):
        """从文档块创建实体"""
        # 批量插入优化
        query = """
        UNWIND $chunks AS chunk
        MERGE (c:Chunk {id: chunk.id})
        SET c.text = chunk.text,
            c.metadata = chunk.metadata
        """
        self.graph.query(query, parameters={"chunks": [chunk.__dict__ for chunk in chunks]})
```

## 🔧 关键实现细节

### 1. 文档处理流水线

#### 分块上传机制
```python
# src/main.py - 大文件分块上传
def upload_file(graph, model, file, chunkNumber, totalChunks, originalname, uri, CHUNK_DIR, MERGED_DIR):
    # 1. 为每个文件创建唯一子目录
    chunk_subdir = os.path.join(CHUNK_DIR, originalname)
    os.makedirs(chunk_subdir, exist_ok=True)
    
    # 2. 保存当前块
    chunk_filename = f"chunk_{chunkNumber}_{totalChunks}"
    chunk_path = os.path.join(chunk_subdir, chunk_filename)
    
    # 3. 检查所有块是否接收完毕
    if len(chunk_files) == int(totalChunks):
        # 4. 合并所有块
        merged_file_path = os.path.join(MERGED_DIR, originalname)
        # 执行文件合并...
        
        # 5. 创建源节点
        obj_source_node = sourceNode()
        obj_source_node.file_name = originalname
        obj_source_node.file_source = 'local file'
        # 设置其他属性...
        graphDb_data_Access = graphDBdataAccess(graph)
        graphDb_data_Access.create_source_node(obj_source_node)
```

#### 智能分块策略
- **按大小分块**：默认5MB为一个块
- **语义分块**：保留文档的语义完整性
- **重叠分块**：块之间有重叠，避免边界信息丢失

### 2. 知识图谱构建引擎

#### Schema 驱动的设计
```python
# src/domain/fault_diagnosis_schema.py - 故障诊断专用Schema
AEROSPACE_FAULT_DIAGNOSIS_NODE_LABELS = {
    # 设备与组件
    "Equipment": "主要设备或系统",
    "Component": "子组件",
    "Subsystem": "子系统",
    
    # 故障相关
    "Fault": "故障现象",
    "FailureMode": "故障模式",
    "Symptom": "故障症状",
    
    # 诊断相关
    "Diagnosis": "诊断结果",
    "Solution": "解决方案",
    "Procedure": "操作程序"
}

# 关系类型定义
AEROSPACE_FAULT_DIAGNOSIS_RELATIONSHIP_TYPES = {
    "CONTAINS": "设备包含组件",
    "CAUSES": "故障导致后果",
    "DIAGNOSES_AS": "诊断为",
    "RESOLVES": "解决问题"
}
```

#### LLM 实体提取
```python
# generate_graphDocuments_from_llm.py
async def extract_entities_with_llm(text: str, model: str, allowed_nodes: List[str]):
    """使用LLM提取实体"""
    prompt = f"""
    从以下文本中提取实体，只返回允许的节点类型：
    {allowed_nodes}
    
    文本：{text}
    
    返回格式：JSON
    """
    
    # 调用LLM API
    response = await llm.generate(prompt)
    
    # 解析结果并创建实体
    entities = json.loads(response.content)
    return [Entity(**entity) for entity in entities]
```

### 3. 多模式查询系统

#### 混合检索实现
```python
# src/QA_integration_new.py
class HybridSearchEngine:
    def __init__(self, graph, vector_store):
        self.graph = graph
        self.vector_store = vector_store
    
    async def search(self, query: str, mode: str = "graph+vector"):
        if mode == "vector":
            # 向量相似度检索
            results = await self.vector_store.similarity_search(query, k=5)
        elif mode == "graph":
            # 图谱结构查询
            results = await self.graph_query(query)
        elif mode == "graph+vector":
            # 混合检索
            vector_results = await self.vector_store.similarity_search(query, k=3)
            graph_results = await self.graph_query(query)
            # 融合结果...
            results = self.merge_results(vector_results, graph_results)
        
        return results
```

### 4. 图像分析集成

#### 多模态处理
```python
# src/image_analysis.py
class ImageAnalyzer:
    def __init__(self):
        self.vlm_model = "glm-4.6v"  # 视觉语言模型
    
    async def analyze_image(self, image_url: str, context: str = None):
        """分析图像内容"""
        # 1. 下载图像
        image_data = await download_image(image_url)
        
        # 2. 构建提示词
        prompt = self.build_analysis_prompt(image_data, context)
        
        # 3. 调用VLM API
        response = await call_vlm_api(prompt)
        
        # 4. 解析结果并创建实体
        entities = parse_vlm_response(response)
        
        return entities
```

### 5. 性能优化策略

#### 并发处理
```python
# 使用 asyncio.gather 实现并发处理
async def process_multiple_documents(documents):
    tasks = [process_document(doc) for doc in documents]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# 批量数据库操作
def batch_create_entities(entities, batch_size=100):
    """批量创建实体，提高性能"""
    for i in range(0, len(entities), batch_size):
        batch = entities[i:i + batch_size]
        query = build_batch_insert_query(batch)
        graph.query(query)
```

#### 缓存机制
```python
# 使用 LRU 缓存缓存 LLM 响应
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_llm_response(prompt: str, model: str):
    """缓存LLM响应，避免重复调用"""
    return call_llm_api(prompt, model)
```

## 🚀 核心功能

### 1. 多模型 LLM 集成
- **GLM-4 & GLM-4.6v**: 智谱AI的通用大语言模型和视觉大模型
- **DeepSeek**: 深度求索大模型
- **Qwen**: 通义千问大模型
- **Ollama**: 本地部署的LLM模型
- **其他模型**: 支持 OpenAI、Azure、Gemini、Anthropic 等模型

### 2. 航空航天机械故障诊断专用 Schema
- **设备组件层次**: Equipment, Component, Subsystem, Part
- **故障类型**: Fault, FailureMode, Symptom, Error, Anomaly, Defect
- **诊断维修**: Diagnosis, Solution, Maintenance, Repair, Procedure
- **监测参数**: Parameter, Sensor, Threshold, Measurement, Indicator
- **原因分析**: Cause, Condition, Trigger, Risk, SafetyIssue
- **文档标准**: Document, Manual, Regulation, Standard, Specification

### 3.Docker 部署
- **docker**: 采用虚拟容器化部署的方法,将数据库灵活部署，利于维护     
  neo4j:
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=apoc
    ports:
      - "7476:7474"
      - "7689:7687"
    volumes:
      - neo4j_data:/data
      
  minio:
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

### 4. 图像解析与存储
- **图像上传**: 支持多种图像格式上传（PNG, JPG, JPEG等）
- **MinIO集成**: 图像文件自动存储到MinIO对象存储
- **视觉分析**: 使用GLM-4.6v模型进行图像内容分析
- **图文关联**: 图像与文档、文档片段自动建立关联关系

### 5. 知识图谱构建
- **实体提取**: 从文本中自动识别设备、故障、症状等实体
- **关系抽取**: 提取实体间的因果关系、组成关系、诊断关系等
- **属性标注**: 为实体添加属性信息（型号、序列号、严重程度等）
- **增量更新**: 支持图谱的增量更新和扩展

### 6. 多源数据支持
- **本地文件**: 支持PDF、TXT、DOC等格式
- **Web页面**: 支持URL直接导入
- **分块上传**: 支持大文件分块上传和处理

### 7. 智能查询与交互
- **向量检索**: 基于语义相似度的文档检索
- **图谱查询**: 基于知识图谱的结构化查询
- **混合模式**: 结合向量检索和图谱查询的混合模式
- **图像分析**: 支持图像内容的智能问答

## 🛠️ 技术栈

### 核心框架
- **FastAPI 0.111.0** - 现代高性能 Web 框架
- **Python 3.8+** - 编程语言
- **Uvicorn** - ASGI 服务器

### 数据库与存储
- **Neo4j 5.15+** - 图数据库（需要安装APOC插件）
- **MinIO** - 对象存储服务（可选）
- **SQLite/PostgreSQL** - 本地存储（通过LangChain）

### LLM 与向量处理
- **LangChain 0.2.6** - LLM 应用开发框架,提供以下组件     
      ├── 文档加载 (PyMuPDFLoader, UnstructuredFileLoader)
      ├── 文档分块 (TokenTextSplitter)
      ├── LLM 接口 (ChatOpenAI)
      ├── 向量化 (SentenceTransformer/OpenAI embeddings)
      ├── 图谱提取 (LLMGraphTransformer)
      └── 向量检索 (Neo4jVector)
- **ZhipuAI** - 智谱AI模型接口
- **Sentence Transformers** - 句子向量模型
- **FAISS** - 向量索引库

### 文档处理
- **PyPDF2 / PyPDFium2** - PDF 文件处理
- **pdfplumber** - PDF 内容提取
- **PyMuPDF** - PDF 高级处理
- **unstructured** - 非结构化数据处理

### 图像处理
- **Pillow** - 图像处理库
- **opencv-python** - 计算机视觉库
- **pytesseract** - OCR 文字识别

### 工具库
- **pydantic** - 数据验证和序列化
- **python-dotenv** - 环境变量管理
- **aiohttp** - 异步HTTP客户端
- **tqdm** - 进度条显示
- **logging** - 日志记录

## 📡 API 接口文档

### 基础服务

#### 1. 健康检查
```http
GET /health
```
响应服务状态信息

#### 2. 数据库连接测试
```http
POST /connect
```
参数：
- `uri`: Neo4j 数据库URI
- `userName`: 用户名
- `password`: 密码（base64编码）
- `database`: 数据库名（可选）

### 文档处理

#### 3. 文件上传（分块）
```http
POST /upload
```
支持大文件分块上传，自动合并并创建源节点。

参数：
- `file`: 文件块
- `chunkNumber`: 当前块编号
- `totalChunks`: 总块数
- `originalname`: 原始文件名
- `model`: 使用的LLM模型
- `uri`: 数据库URI
- `userName`: 用户名
- `password`: 密码

#### 4. 知识图谱提取
```http
POST /extract
```
从文档中提取知识图谱。

参数：
- `uri`: 数据库URI
- `userName`: 用户名
- `password`: 密码
- `model`: LLM模型名称
- `database`: 数据库名
- `source_url`: 文档源URL（用于web源）
- `source_type`: 源类型（'local file' 或 'web-url'）
- `file_name`: 文件名
- `allowedNodes`: 允许的节点类型（JSON数组）
- `allowedRelationship`: 允许的关系类型（JSON数组）
- `language`: 语言（可选）

#### 5. Web URL 扫描
```http
POST /url/scan
```
扫描Web URL并创建知识图谱。

参数：
- `uri`: 数据库URI
- `userName`: 用户名
- `password`: 密码
- `source_url`: Web URL
- `source_type`: 'web-url'
- `database`: 数据库名
- `model`: 使用的模型

#### 6. 源列表查询
```http
GET /sources_list
```
获取已存在于数据库中的数据源列表。

参数：
- `uri`: 数据库URI
- `userName`: 用户名
- `password`: 密码
- `database`: 数据库名（可选）

### 图谱查询

#### 7. 图谱模式查询
```http
POST /schema
```
获取数据库中的节点标签和关系类型。

参数：
- `uri`: 数据库URI
- `userName`: 用户名
- `password`: 密码
- `database`: 数据库名

#### 8. 图谱结果查询
```http
POST /graph_query
```
执行图谱查询并返回结果。

参数：
- `uri`: 数据库URI
- `userName`: 用户名
- `password`: 密码
- `document_names`: 文档名称列表（JSON数组）

#### 9. Chunk 实体查询
```http
POST /chunk_entities
```
根据chunk ID获取相关实体。

参数：
- `uri`: 数据库URI
- `userName`: 用户名
- `password`: 密码
- `chunk_ids`: chunk ID列表（逗号分隔）

### 智能对话

#### 10. 聊天机器人
```http
POST /chat_bot
```
多模式智能问答。

参数：
- `uri`: 数据库URI
- `userName`: 用户名
- `password`: 密码
- `database`: 数据库名
- `model`: 使用的模型
- `question`: 用户问题
- `document_names`: 文档名称列表（JSON）
- `session_id`: 会话ID
- `mode`: 模式（'vector', 'graph', 'graph+vector', 'image+graph+vector'）
- `image_url`: 图像URL（可选）

#### 11. 清除聊天历史
```http
POST /clear_chat_bot
```
清除指定会话的聊天历史。

参数：
- `uri`: 数据库URI
- `userName`: 用户名
- `password`: 密码
- `database`: 数据库名
- `session_id`: 会话ID

### 图像处理

#### 12. 图像列表获取
```http
GET /images_list
```
获取图像列表及其关联的chunks。

参数：
- `uri`: 数据库URI
- `userName`: 用户名
- `password`: 密码
- `database`: 数据库名
- `document_names`: 文档名称列表（JSON，可选）

#### 13. 图像分析
```http
POST /image/analyze
```
使用GLM-4.6v分析图像内容。

参数：
- `image_url`: 图像URL
- `model`: 使用的模型
- `context`: 上下文信息（可选）

### 后处理

#### 14. 后处理任务
```http
POST /post_processing
```
执行图谱后处理任务。

参数：
- `uri`: 数据库URI
- `userName`: 用户名
- `password`: 密码
- `database`: 数据库名
- `tasks`: 任务列表（JSON数组）
  - `update_similarity_graph`: 更新相似度图谱
  - `create_fulltext_index`: 创建全文索引
  - `create_entity_embedding`: 创建实体嵌入

#### 15. 文档状态更新（SSE）
```http
GET /update_extract_status/{file_name}
```
服务器发送事件，实时更新文档处理状态。

参数（查询）：
- `url`: 数据库URI
- `userName`: 用户名
- `password`: 密码
- `database`: 数据库名

#### 16. 文档状态查询
```http
GET /document_status/{file_name}
```
查询文档当前处理状态。

### 数据管理

#### 17. 删除文档和实体
```http
POST /delete_document_and_entities
```
删除文档及其关联的实体。

参数：
- `uri`: 数据库URI
- `userName`: 用户名
- `password`: 密码
- `database`: 数据库名
- `filenames`: 文件名列表（JSON数组）
- `source_types`: 源类型列表（JSON数组）
- `deleteEntities`: 是否删除实体（布尔值）

#### 18. 取消运行中的任务
```http
POST /cancelled_job
```
取消正在运行的处理任务。

#### 19. 孤立节点管理
```http
POST /get_unconnected_nodes_list
```
获取孤立节点列表。

#### 20. 删除孤立节点
```http
POST /delete_unconnected_nodes
```
删除选定的孤立节点。

### 高级功能

#### 21. Schema 生成
```http
POST /populate_graph_schema
```
从文本生成图谱Schema。

参数：
- `input_text`: 输入文本
- `model`: 使用的模型
- `is_schema_description_checked`: 是否包含Schema描述

## ⚙️ 配置说明

### 环境变量配置

创建 `.env` 文件：

```env
# Neo4j 数据库配置
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# GLM 模型配置
ZHIPUAI_API_KEY=your_glm_api_key
ZHIPUAI_API_URL=https://open.bigmodel.cn/api/paas/v4
V_ZHIPUAI_API_KEY=your_v_glm_api_key
V_ZHIPUAI_API_URL=https://open.bigmodel.cn/api/paas/v4

# DeepSeek 配置
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_API_URL=https://api.deepseek.com

# Qwen 配置
QWEN_API_KEY=your_qwen_key
QWEN_API_URL=https://dashscope.aliycs.com

# OpenAI 配置（可选）
OPENAI_API_KEY=your_openai_key

# MinIO 配置（可选）
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=llm-graph-images
MINIO_USE_SSL=false

# 嵌入模型配置
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# 处理配置
CHUNK_SIZE=5242880
NUMBER_OF_CHUNKS_TO_COMBINE=5
UPDATE_GRAPH_CHUNKS_PROCESSED=20

# 服务配置
TCP_PORT=8000
ENV=DEV
```

### 模型配置

支持的模型版本：

| 模型名称 | 环境变量前缀 | 模型类型 | 用途 |
|---------|-------------|---------|------|
| GLM | LLM_MODEL_CONFIG_GLM | 文本模型 | 通用文本处理 |
| v-GLM | LLM_MODEL_CONFIG_v-GLM | 视觉模型 | 图像分析 |
| DeepSeek | LLM_MODEL_CONFIG_深度求索 | 文本模型 | 故障诊断分析 |
| Qwen | LLM_MODEL_CONFIG_通义千问 | 文本模型 | 技术文档理解 |
| Ollama | LLM_MODEL_CONFIG_Ollama | 文本模型 | 本地部署 |

### 故障诊断 Schema

#### 节点类型
- **Equipment**: 主设备（发动机、起落架等）
- **Component**: 组件（泵、阀门、传感器等）
- **Fault**: 故障现象
- **FailureMode**: 故障模式
- **Symptom**: 故障症状
- **Diagnosis**: 诊断结果
- **Solution**: 解决方案
- **Parameter**: 监测参数
- **Sensor**: 传感器
- **Document**: 文档

#### 关系类型
- **CONTAINS**: 设备包含组件
- **CAUSES**: 故障导致后果
- **DIAGNOSES_AS**: 诊断为
- **RESOLVES**: 解决问题
- **MONITORS**: 监测参数

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd llm-graph-builder/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入必要的配置
```

### 3. 启动服务

```bash
# 开发模式
uvicorn score:app --reload --host 0.0.0.0 --port 8000

# 生产模式
gunicorn score:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 4. 访问文档

打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 项目结构

```
backend/
├── score.py              # FastAPI 应用主入口
├── requirements.txt      # Python 依赖
├── .env                # 环境变量配置
├── src/                # 源代码目录
│   ├── llm.py          # LLM 模型封装
│   ├── llm_api_request.py # LLM API 请求封装
│   ├── main.py         # 主要业务逻辑
│   ├── QA_integration_new.py # 新版 QA 集成
│   ├── image_analysis.py     # 图像分析模块
│   ├── storage/        # 存储相关
│   │   └── minio_client.py  # MinIO 客户端
│   ├── graph_transformers/   # 图谱转换器
│   │   └── llm.py     # LLM 图谱转换
│   ├── domain/         # 领域特定
│   │   ├── fault_diagnosis_schema.py  # 故障诊断 Schema
│   │   └── fault_diagnosis_prompts.py # 故障诊断提示词
│   ├── shared/         # 共享模块
│   │   ├── constants.py      # 常量定义
│   │   ├── common_fn.py     # 通用函数
│   │   └── schema_extraction.py # Schema 提取
│   ├── graphDB_dataAccess.py  # 数据库访问层
│   ├── graph_query.py  # 图谱查询
│   ├── create_chunks.py    # 文档分块
│   ├── generate_graphDocuments_from_llm.py # 生成图谱文档
│   ├── make_relationships.py  # 创建关系
│   ├── post_processing.py    # 后处理
│   ├── api_response.py      # API 响应格式
│   └── logger.py            # 日志配置
├── chunks/            # 文档分块临时目录
└── merged_files/      # 合并后的文件存储目录
```

## 🔧 开发指南

### 添加新的 LLM 模型

1. 在 `src/llm.py` 的 `get_llm` 函数中添加新模型的初始化代码
2. 在 `src/shared/constants.py` 中添加模型版本配置
3. 更新环境变量配置模板

### 添加新的节点/关系类型

1. 在 `src/domain/fault_diagnosis_schema.py` 中定义新的类型
2. 更新默认允许的节点和关系列表
3. 更新前端配置以支持新类型

### 自定义处理流程

1. 在 `src/main.py` 中添加新的处理函数
2. 在 `score.py` 中添加对应的 API 端点
3. 更新文档说明

## 🐛 故障排除

### 常见问题

1. **Neo4j 连接失败**
   - 检查 URI、用户名、密码是否正确
   - 确认 Neo4j 服务正在运行
   - 检查 APOC 插件是否安装

2. **LLM 调用失败**
   - 验证 API 密钥是否正确
   - 检查网络连接
   - 确认模型是否可用

3. **图像处理失败**
   - 检查 MinIO 配置
   - 确认图像格式支持
   - 验证 GLM-4.6v API 密钥

4. **内存不足**
   - 调整 CHUNK_SIZE
   - 减少 NUMBER_OF_CHUNKS_TO_COMBINE
   - 增加系统内存

### 日志配置

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 📊 性能优化

### 1. 并发处理
- 使用 ThreadPoolExecutor 处理多个文档
- 调整 max_workers 参数
- 实现任务队列

### 2. 缓存策略
- 缓存 LLM 响应
- 缓存嵌入向量
- 缓存常用查询结果

### 3. 数据库优化
- 创建适当的索引
- 优化 Cypher 查询
- 定期维护数据库

## 🔒 安全考虑

1. **API 密钥管理**
   - 使用环境变量存储密钥
   - 不要在代码中硬编码密钥
   - 定期轮换密钥

2. **数据安全**
   - 使用 HTTPS 传输
   - 加密敏感数据
   - 实施访问控制

3. **文件上传安全**
   - 验证文件类型
   - 限制文件大小
   - 扫描恶意文件

## 📈 监控与日志

### 日志级别
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- DEBUG: 调试信息

### 性能监控
- 请求响应时间
- 内存使用情况
- 数据库查询性能
- LLM API 调用统计

## 🤝 贡献指南

1. Fork 项目仓库
2. 创建功能分支
3. 提交代码更改
4. 创建 Pull Request

### 代码规范
- 遵循 PEP 8 规范
- 添加适当的注释
- 编写测试用例
- 更新文档

**BUAA_7** 🚀

## 附录

### 环境变量完整列表

| 变量名 | 必需/可选 | 默认值 | 描述 |
|--------|-----------|--------|------|
| NEO4J_URI | 可选 | neo4j://localhost:7687 | Neo4j数据库URI |
| NEO4J_USERNAME | 可选 | neo4j | Neo4j用户名 |
| NEO4J_PASSWORD | 可选 | password | Neo4j密码 |
| NEO4J_DATABASE | 可选 | neo4j | Neo4j数据库名 |
| ZHIPUAI_API_KEY | 可选 | - | GLM API密钥 |
| ZHIPUAI_API_URL | 可选 | https://open.bigmodel.cn/api/paas/v4 | GLM API地址 |
| V_ZHIPUAI_API_KEY | 可选 | - | GLM-4.6V API密钥 |
| V_ZHIPUAI_API_URL | 可选 | https://open.bigmodel.cn/api/paas/v4 | GLM-4.6V API地址 |
| DEEPSEEK_API_KEY | 可选 | - | DeepSeek API密钥 |
| DEEPSEEK_API_URL | 可选 | https://api.deepseek.com | DeepSeek API地址 |
| QWEN_API_KEY | 可选 | - | 通义千问API密钥 |
| QWEN_API_URL | 可选 | https://dashscope.aliyuncs.com | 通义千问API地址 |
| OPENAI_API_KEY | 可选 | - | OpenAI API密钥 |
| MINIO_ENDPOINT | 可选 | localhost:9000 | MinIO服务地址 |
| MINIO_ACCESS_KEY | 可选 | minioadmin | MinIO访问密钥 |
| MINIO_SECRET_KEY | 可选 | minioadmin | MinIO密钥 |
| MINIO_BUCKET_NAME | 可选 | llm-graph-images | MinIO存储桶名称 |
| MINIO_USE_SSL | 可选 | false | 是否使用HTTPS |
| EMBEDDING_MODEL | 可选 | sentence-transformers/all-MiniLM-L6-v2 | 嵌入模型名称 |
| CHUNK_SIZE | 可选 | 5242880 | 文件块大小 |
| NUMBER_OF_CHUNKS_TO_COMBINE | 可选 | 5 | 合并的块数量 |
| TCP_PORT | 可选 | 8000 | 服务端口 |
| ENV | 可选 | DEV | 运行环境 |