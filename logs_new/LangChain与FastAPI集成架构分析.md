# LangChain与FastAPI的集成架构分析

## FastAPI作为Web服务层

FastAPI在这个系统中担任**API网关**的角色，负责：
- 接收HTTP请求
- 参数验证和处理
- 协调LangChain组件
- 返回JSON响应

```python
# FastAPI应用实例
app = FastAPI()

# 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## LangChain作为AI处理层

LangChain负责核心的AI处理逻辑：
- 文档加载和预处理
- 向量化和嵌入
- 知识图谱构建
- 检索增强生成（RAG）

## 关键集成点

### 1. **文档上传与处理集成**

```python
@app.post("/upload")
async def upload_large_file_into_chunks(
    file: UploadFile = File(...),
    chunkNumber=Form(None),
    totalChunks=Form(None),
    originalname=Form(None),
    model=Form(None),
    uri=Form(None),
    userName=Form(None),
    password=Form(None),
    database=Form(None)
):
    try:
        # 1. FastAPI接收文件
        graph = create_graph_database_connection(uri, userName, password, database)
        
        # 2. 调用LangChain处理逻辑
        result = await asyncio.to_thread(
            upload_file, 
            graph, model, file, chunkNumber, totalChunks, 
            originalname, uri, CHUNK_DIR, MERGED_DIR
        )
        
        return create_api_response('Success', data=result)
    except Exception as e:
        return create_api_response('Failed', message=str(e))
```

### 2. **知识图谱提取集成**

```python
@app.post("/extract")
async def extract_knowledge_graph_from_file(
    uri=Form(None),
    userName=Form(None),
    password=Form(None),
    model=Form(None),
    database=Form(None),
    source_url=Form(None),
    source_type=Form(None),
    file_name=Form(None),
    allowedNodes=Form(None),
    allowedRelationship=Form(None),
    language=Form(None)
):
    try:
        graph = create_graph_database_connection(uri, userName, password, database)
        
        if source_type == 'local file':
            # LangChain处理本地文件
            merged_file_path = os.path.join(MERGED_DIR, file_name)
            result = await asyncio.to_thread(
                extract_graph_from_file_local_file,
                graph, model, merged_file_path, file_name, 
                allowedNodes, allowedRelationship, uri
            )
        elif source_type == 'web-url':
            # LangChain处理网页
            result = await asyncio.to_thread(
                extract_graph_from_web_page,
                graph, model, source_url, allowedNodes, allowedRelationship
            )
        
        return create_api_response('Success', data=result)
    except Exception as e:
        return create_api_response('Failed', message=str(e))
```

### 3. **向量数据库集成**

```python
# 在QA_integration_new.py中
def get_neo4j_retriever(graph, retrieval_query, document_names):
    try:
        # LangChain Neo4jVector集成
        neo_db = Neo4jVector.from_existing_index(
            embedding=EMBEDDING_FUNCTION,  # LangChain embedding
            index_name="vector",
            retrieval_query=retrielation_query,
            graph=graph
        )
        
        # 创建检索器
        retriever = neo_db.as_retriever(
            search_kwargs={'k': 3, "score_threshold": 0.7}
        )
        return retriever
    except Exception as e:
        logging.error(f"Error creating retriever: {e}")
        return None
```

### 4. **LLM模型调用集成**

```python
# 在llm.py中
def get_llm(model_version: str):
    """LangChain LLM模型封装"""
    if "Ollama" in model_version:
        llm = ChatOpenAI(
            api_key=os.environ.get('OLLAMA_API_KEY'),
            base_url=os.environ.get('OLLAMA_API_URL'),
            model=model_name,
            temperature=0.98
        )
    elif "gemini" in model_version:
        llm = ChatVertexAI(
            model_name=model_name,
            convert_system_message_to_human=True,
            credentials=credentials,
            project=project_id,
            temperature=0,
            safety_settings={...}
        )
    return llm
```

### 5. **异步处理模式**

FastAPI与LangChain通过异步模式实现高效集成：

```python
# 使用asyncio.to_thread将同步LangChain操作放入线程池
result = await asyncio.to_thread(
    QA_RAG,
    graph=graph,
    model=model,
    question=question,
    document_names=document_names,
    session_id=session_id,
    mode=mode
)
```

### 6. **多模态处理集成**

```python
@app.post("/chat_bot")
async def chat_bot(
    uri=Form(None),
    model=Form(None),
    question=Form(None),
    image_url=Form(None),
    mode=Form(None)
):
    try:
        if mode == "graph":
            graph = Neo4jGraph(url=uri, username=userName, password=password, database=database)
        else:
            graph = create_graph_database_connection(uri, userName, password, database)
        
        # LangChain多模态QA处理
        result = await asyncio.to_thread(
            QA_RAG,
            graph=graph,
            model=model,
            question=question,
            document_names=document_names,
            session_id=session_id,
            mode=mode,
            image_url=image_url
        )
        
        return create_api_response('Success', data=result)
    except Exception as e:
        return create_api_response('Failed', message=str(e))
```

### 7. **LangServe集成**

系统还集成了LangServe，用于LangChain服务的部署：

```python
# 集成LangServe服务
from langserve import add_routes

# 添加VertexAI服务路由
is_gemini_enabled = os.environ.get("GEMINI_ENABLED", "False").lower() in ("true", "1", "yes")
if is_gemini_enabled:
    add_routes(app, ChatVertexAI(), path="/vertexai")
```

### 8. **数据流架构```

```
HTTP请求 (FastAPI)
    ↓
参数验证 & 请求解析
    ↓
异步任务分发 (asyncio.to_thread)
    ↓
LangChain组件处理
    ├── 文档加载 (PyMuPDFLoader, UnstructuredFileLoader)
    ├── 文档分块 (TokenTextSplitter)
    ├── 向量化 (SentenceTransformer/OpenAI embeddings)
    ├── 图谱提取 (LLMGraphTransformer)
    └── 向量检索 (Neo4jVector)
    ↓
Neo4j数据库存储
    ↓
JSON响应 (FastAPI)
```

### 9. **关键优势**

1. **解耦架构**：
   - FastAPI负责HTTP层
   - LangChain负责AI处理逻辑
   - 两者通过清晰的接口交互

2. **异步支持**：
   - FastAPI原生支持异步
   - 使用`asyncio.to_thread`处理阻塞的LangChain操作

3. **错误处理**：
   - 统一的错误响应格式
   - 完整的异常捕获机制

4. **扩展性**：
   - 易于添加新的API端点
   - LangChain组件可独立升级

5. **类型安全**：
   - FastAPI的Pydantic模型验证
   - LangChain的类型提示支持

这种架构充分利用了FastAPI的高性能特性和LangChain的强大AI能力，实现了高效的知识图谱构建和问答系统。