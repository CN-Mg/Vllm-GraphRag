# 知识图谱构建平台 - 航空航天机械故障诊断

## 项目概述

这是一个专门为航空航天机械故障诊断与健康管理（PHM）领域设计的知识图谱构建平台。该平台能够将非结构化的技术文档、维修手册、故障报告等数据，通过大语言模型（LLM）转换为结构化的知识图谱，存储在Neo4j数据库中，支持智能查询、可视化和诊断分析。

## 🎯 核心价值

本平台解决了航空航天领域故障诊断中的关键痛点：
- **数据孤岛问题**：具备将多个分散的技术文档、维修记录整合为统一知识图谱
- **诊断效率提升**：基于LLM的智能问答，快速定位故障原因和解决方案
- **知识传承**：将专家经验结构化存储，便于新人员学习和培训
- **预测性维护**：通过参数监测和趋势分析，实现故障预测

## 🚀 核心特性

### 1. 多模型支持
- **GLM-4 & GLM-4.6v**: 智谱AI的通用大语言模型和视觉大模型
- **DeepSeek**: 深度求索大模型
- **Qwen**: 通义千问大模型
- **Ollama**: 本地部署的LLM模型

### 2. 航空航天机械故障诊断专用Schema
- **设备组件层次**: Equipment, Component, Subsystem, Part
- **故障类型**: Fault, FailureMode, Symptom, Error, Anomaly, Defect
- **诊断维修**: Diagnosis, Solution, Maintenance, Repair, Procedure
- **监测参数**: Parameter, Sensor, Threshold, Measurement, Indicator
- **原因分析**: Cause, Condition, Trigger, Risk, SafetyIssue
- **文档标准**: Document, Manual, Regulation, Standard, Specification

### 3. 图像解析与存储
- **图像上传**: 支持多种图像格式上传（PNG, JPG, JPEG等）
- **MinIO集成**: 图像文件自动存储到MinIO对象存储
- **视觉分析**: 使用GLM-4.6v模型进行图像内容分析
- **图文关联**: 图像与文档、文档片段自动建立关联关系

### 4. 知识图谱构建
- **实体提取**: 从文本中自动识别设备、故障、症状等实体
- **关系抽取**: 提取实体间的因果关系、组成关系、诊断关系等
- **属性标注**: 为实体添加属性信息（型号、序列号、严重程度等）
- **增量更新**: 支持图谱的增量更新和扩展

### 5. 多源数据支持
- **本地文件**: 支持PDF、TXT、DOC等格式
- **Web页面**: 支持开放式网址URL直接导入
- **API接口**: 提供RESTful API供外部系统集成

### 6. 智能查询与交互问答
- **向量检索**: 基于语义相似度的文档检索
- **图谱查询**: 基于知识图谱的结构化查询
- **混合模式**: 结合 向量检索 和 图谱查询 的混合模式
- **图像分析**: 支持图像内容的智能问答

## 🏗️ 架构设计

### 系统架构图
```
┌─────────────────────────────────────────────────────────┐
│                   用户界面层                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   React     │  │   Material  │  │   Neo4j     │  │
│  │    UI       │  │    UI       │  │   Bloom     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                  业务逻辑层                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  文件处理   │  │  图谱生成   │  │  智能对话   │  │
│  │  组件       │  │  引擎       │  │  系统       │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   服务层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   FastAPI   │  │   LLM API   │  │   MinIO     │  │
│  │    接口      │  │   集成      │  │    存储     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   数据层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Neo4j     │  │   LangChain │  │   本地文件   │  │
│  │   知识图谱   │  │    框架     │  │    系统     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 关键技术实现思路

#### 1. 多LLM模型集成架构
- **统一接口层**：在 `src/llm.py` 中实现 `get_llm()` 函数，支持多种LLM模型的统一调用
- **动态配置**：通过环境变量配置不同模型的API密钥和参数
- **负载均衡**：根据模型类型自动选择合适的模型进行特定任务（如GLM-4.6v用于图像分析）

#### 2. 文档处理流水线
- **分块上传**：大文件通过 `POST /upload` 分块上传，避免文件大小限制
- **智能分块**：在 `src/create_chunks.py` 中实现基于语义的文档分块
- **增量处理**：支持断点续传和增量更新，提高处理效率

#### 3. 知识图谱构建引擎
- **Schema定义**：`src/domain/fault_diagnosis_schema.py` 定义了航空航天领域的专用Schema
- **实体提取**：使用LLM从文本中提取实体和关系
- **图谱优化**：通过 `src/post_processing.py` 实现相似度图谱、全文索引等优化

#### 4. 智能问答系统
- **多模式查询**：支持Vector、Graph、Graph+Vector、Image+Graph+Vector四种查询模式
- **上下文管理**：使用session ID维护对话上下文
- **响应生成**：结合图谱查询结果和LLM生成自然语言回答

## 🔧 核心技术实现详解

### 1. 文档处理流水线
```mermaid
graph LR
    A[文件上传] --> B[分块处理]
    B --> C[内容提取]
    C --> D[文本分块]
    D --> E[LLM实体提取]
    E --> F[关系抽取]
    F --> G[图谱构建]
    G --> H[存储优化]
```

**实现细节**：
- **分块上传**：`src/main.py` 中的 `upload_file()` 函数处理大文件分块
- **内容提取**：支持PDF（PyPDF2/PDFium2）、TXT、DOC等多种格式
- **文本处理**：使用LangChain的DocumentLoader进行结构化提取

### 2. 知识图谱构建引擎
```python
# Schema定义示例（src/domain/fault_diagnosis_schema.py）
AEROSPACE_FAULT_DIAGNOSIS_NODE_LABELS = {
    "Equipment": "主要设备或系统",
    "Fault": "故障现象",
    "Symptom": "故障症状",
    "Diagnosis": "诊断结果",
    "Solution": "解决方案"
}

# 关系类型
AEROSPACE_FAULT_DIAGNOSIS_RELATIONSHIP_TYPES = {
    "CONTAINS": "包含关系",
    "CAUSES": "因果关系",
    "DIAGNOSES_AS": "诊断关系",
    "RESOLVES": "解决关系"
}
```

### 3. 多LLM集成架构
```python
# src/llm.py - 模型统一接口
def get_llm(model_name: str):
    if model_name == "GLM":
        return ChatZhipuAI(model="glm-4.5-flash", api_key=zhipu_api_key)
    elif model_name == "DeepSeek":
        return ChatDeepSeekAI(model="deepseek-chat", api_key=deepseek_api_key)
    elif model_name == "Qwen":
        return ChatQianwenAI(model="qwen-long", api_key=qwen_api_key)
    # 更多模型...
```

### 4. 智能问答系统
```python
# src/QA_integration_new.py - 查询逻辑
def chat_query(question, mode="graph+vector"):
    if mode == "vector":
        # 基于向量相似度检索
        results = vector_search(question)
    elif mode == "graph":
        # 基于图谱结构查询
        results = graph_query(question)
    elif mode == "graph+vector":
        # 混合模式
        results = hybrid_search(question)
    return generate_response(results, question)
```

### 5. 前端组件架构
```typescript
// 主要组件层次
App
├── QuickStarter          // 快速启动组件
├── PageLayout           // 主布局组件
│   ├── Sidebar         // 侧边栏
│   ├── MainContent     // 主内容区
│   └── ChatDrawer      // 聊天抽屉
├── DataSources         // 数据源组件
│   ├── Local/DropZone  // 本地文件上传
│   └── WebSources      // Web URL导入
└── GraphComponents     // 图谱可视化组件
    ├── GraphViewModal  // 图谱视图模态框
    └── LegendsChip     // 图例组件
```

## 📦 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Neo4j 5.15+ (需要安装APOC插件)
- MinIO (可选，用于图像存储)

### 本地部署

#### 1. 克隆项目
```bash
git clone <repository-url>
cd llm-graph-builder
```

#### 2. 配置环境变量

创建 `.env` 文件：

```env
# Neo4j 配置
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# GLM 配置
ZHIPUAI_API_KEY=your_glm_api_key
ZHIPUAI_API_URL=https://open.bigmodel.cn/api/paas/v4

# GLM-4.6V 视觉模型配置
V_ZHIPUAI_API_KEY=your_v_glm_api_key
V_ZHIPUAI_API_URL=https://open.bigmodel.cn/api/paas/v4

# MinIO 配置 (可选)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=llm-graph-images
MINIO_USE_SSL=false

# 其他模型配置 (可选)
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_API_URL=https://api.deepseek.com
QWEN_API_KEY=your_qwen_key
QWEN_API_URL=https://dashscope.aliyuncs.com

# OpenAI 配置 (可选)
OPENAI_API_KEY=your_openai_key

# Chunk 处理配置
CHUNK_SIZE=5242880
NUMBER_OF_CHUNKS_TO_COMBINE=5
UPDATE_GRAPH_CHUNKS_PROCESSED=20
```

#### 3. 启动后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn score:app --reload
```

#### 4. 启动前端
```bash
cd frontend
npm install
npm run dev
```

### Docker 部署

```bash
# 构建并启动所有服务
docker-compose up --build
```

## 🔧 配置说明

### 支持的LLM模型

| 模型名称 | 模型版本 | 用途 |
|---------|---------|------|
| GLM | glm-4.5-flash | 通用文本处理 |
| v-GLM | glm-4.6v | 视觉分析和图像理解 |
| 深度求索 | deepseek-chat | 故障诊断分析 |
| 通义千问 | qwen-long | 技术文档理解 |
| Ollama | qwen3:8b | 本地部署 |

### 数据源配置

默认支持的数据源：
- `local`: 本地文件上传
- `web`: 网页URL导入

可通过环境变量 `REACT_APP_SOURCES` 配置：
```env
REACT_APP_SOURCES="local,web"
```

### 聊天模式配置

支持三种聊天模式：
- `vector`: 向量检索模式
- `graph`: 图谱查询模式
- `graph+vector`: 混合检索模式
- `image+graph+vector`: 图像+图谱+向量混合模式

```env
CHAT_MODES="vector,graph+vector,image+graph+vector"
```

## 📊 使用指南

### 1. 上传文档
- 支持格式：PDF、TXT、DOC等
- 拖拽上传或点击选择文件
- 批量上传支持

### 2. 配置Schema
- 选择预设的故障诊断Schema
- 自定义节点类型和关系类型
- 配置属性模板

### 3. 生成知识图谱
- 选择使用的LLM模型
- 设置处理参数
- 开始图谱构建

### 4. 查询与分析
- 使用自然语言查询
- 查看图谱可视化
- 分析故障模式

### 5. 图像分析
- 上传图像文件
- 使用GLM-4.6v进行视觉分析
- 查看分析结果和建议

## 🛠️ API接口

### 主要端点

#### 文档处理
- `POST /api/upload`: 文件上传
- `GET /api/documents`: 获取文档列表
- `POST /api/process`: 处理文档生成图谱

#### 图谱查询
- `GET /api/graph/entities`: 查询实体
- `GET /api/graph/relationships`: 查询关系
- `GET /api/graph/paths`: 查询路径

#### 智能问答
- `POST /api/chat/chat`: 聊天查询
- `POST /api/chat/chat_with_image`: 图像聊天

#### 图像处理
- `POST /api/image/upload`: 图像上传
- `GET /api/image/list`: 获取图像列表
- `POST /api/image/analyze`: 图像分析

## 🔒 安全配置

### 敏感信息保护
- 所有API密钥通过环境变量配置
- 支持HTTPS加密传输
- MinIO访问控制配置

### 隐私保护建议
1. 不要在代码中硬编码API密钥
2. 定期更换API密钥
3. 使用HTTPS协议
4. 限制文件上传大小和类型
5. 实施访问控制和身份验证

## 📈 性能优化

### 处理优化
- Chunk大小调整
- 并行处理配置
- 缓存策略

### 存储优化
- 图谱索引优化
- 数据分片策略
- 定期清理

## 🐛 故障排除

### 常见问题
1. **Neo4j连接失败**: 检查URI、用户名、密码
2. **LLM调用失败**: 验证API密钥和网络连接
3. **图像处理失败**: 检查MinIO配置和文件格式
4. **内存不足**: 调整chunk大小和并发数

### 日志配置
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🔗 相关链接

- [Neo4j官方文档](https://neo4j.com/docs/)
- [GLM模型文档](https://open.bigmodel.cn/)
- [MinIO官方文档](https://min.io/docs/)
- [LangChain文档](https://python.langchain.com/)

## 📄 许可证

本项目遵循 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献指南

欢迎提交Issue和Pull Request来贡献代码。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 [GitHub Issue]
- 发送邮件至：17880994783@163.com

---

## 📚 附录

### 环境变量完整列表

| 变量名 | 必需/可选 | 默认值 | 描述 |
|--------|-----------|--------|------|
| NEO4J_URI | 可选 | neo4j://localhost:7687 | Neo4j数据库URI |
| NEO4J_USERNAME | 可选 | neo4j | Neo4j用户名 |
| NEO4J_PASSWORD | 可选 | password | Neo4j密码 |
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
| CHUNK_SIZE | 可选 | 5242880 | 文件块大小 |
| NUMBER_OF_CHUNKS_TO_COMBINE | 可选 | 5 | 合并的块数量 |
| UPDATE_GRAPH_CHUNKS_PROCESSED | 可选 | 20 | 更新进度处理的块数量 |
| REACT_APP_SOURCES | 可选 | local,web | 支持的数据源 |
| CHAT_MODES | 可选 | vector,graph+vector,image+graph+vector | 聊天模式 |
| ENV | 可选 | DEV | 运行环境 |

### 故障诊断Schema详解

#### 节点类型详解
- **Equipment**: 主设备（如发动机、起落架）
- **Component**: 组件（如泵、阀门、传感器）
- **Fault**: 故障现象
- **FailureMode**: 故障模式
- **Symptom**: 故障症状
- **Diagnosis**: 诊断结果
- **Solution**: 解决方案

#### 关系类型详解
- **CONTAINS**: 设备包含组件
- **CAUSES**: 故障导致后果
- **DIAGNOSES_AS**: 诊断为
- **RESOLVES**: 解决问题
- **MONITORS**: 监测参数

---

## 💡 项目亮点与技术优势

### 1. 领域专用 Schema 设计
- **专业定制**：针对航空航天故障诊断领域专门设计的 Schema
- **灵活扩展**：支持自定义节点类型和关系类型
- **语义丰富**：包含设备、故障、诊断、维修等完整业务实体

### 2. 多模态智能处理
- **文本理解**：支持多种文档格式的智能解析
- **图像分析**：集成 GLM-4.6v 视觉模型，支持图像内容分析
- **多模态融合**：结合文本、图像、图谱的混合检索模式

### 3. 高性能架构设计
- **异步处理**：基于 FastAPI 的异步架构，支持高并发
- **分块上传**：支持大文件分块上传，避免内存限制
- **缓存优化**：智能缓存 LLM 响应和查询结果

### 4. 开放与可扩展
- **多模型支持**：支持 GLM、DeepSeek、Qwen、Ollama 等多种 LLM
- **标准接口**：提供完整的 RESTful API，便于集成
- **容器化部署**：支持 Docker 和 docker-compose 一键部署

### 5. 用户体验优化
- **直观操作**：拖拽上传、实时进度反馈
- **可视化展示**：基于 Neo4j 的图谱可视化
- **智能交互**：多模式对话，支持语音合成

## 🚀 应用场景

### 1. 航空维修支持
- 快速定位故障原因
- 查询维修手册和标准程序
- 推荐最佳解决方案

### 2. 设备健康管理
- 监测设备运行参数
- 预测潜在故障
- 制定维护计划

### 3. 知识管理
- 构建企业知识库
- 专家经验传承
- 培训新员工

### 4. 故障分析
- 统计故障模式
- 分析故障原因
- 改进设计缺陷

## 🎯 项目路线图

### 已完成功能
- [√] 基础知识图谱构建
- [√] 多LLM模型集成（GLM、DeepSeek、Qwen、Ollama）
- [√] 图像解析与存储
- [√] 故障诊断专用 Schema
- [√] MinIO 对象存储集成
- [√] 高级可视化功能
- [√] 智能问答系统
- [√] 文档分块与增量处理
- [√] 实时进度反馈
- [√] 多语言界面支持

### 计划中功能
- [ ] 移动端适配（PWA）
- [ ] 企业级部署方案（Kubernetes）
- [ ] 高级权限管理
- [ ] 数据血缘分析
- [ ] 知识推理引擎
- [ ] 性能监控仪表板
- [ ] 图谱版本管理
- [ ] 自动化测试框架

## 🤝 参与贡献

### 如何贡献
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范
- 遵循 PEP 8（Python）和 ESLint（TypeScript）
- 编写测试用例
- 更新相关文档
- 确保代码通过 CI/CD 检查

### 交流社区
- 提交 GitHub Issue
- 参与讨论
- 分享使用经验

---

## 📄 许可证

本项目遵循 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 [GitHub Issue]
- 发送邮件至：17880994783@163.com
- 项目负责人：BUAA_7

---

**🎯 使命**：让知识图谱构建变得简单高效，助力航空航天领域智能化升级

**🚀 愿景**：成为工业领域知识图谱构建的领先解决方案

一、参考我自己写的，上传到github代码仓库，牢牢结合我的代码核心技术路线，形成一份满足985机械工程及自动化学院智能制造工程的最终本科毕业论文,有足够的篇幅、公式、核心算法、良好的格式等等。

二、论文题目是：基于多模态大语言模型的故障诊断知识图谱构建技术
毕设主要包括三项研究内容：
1、非结构化故障信息的抽取模型构建
针对维修报告、图像等信息，研究并构建一种能够
自动识别故障设备、部件、现象与原因等关键实体及其语义关系的抽取模型，为知识结构化奠定基础。
2、故障知识图谱构建与存储
基于抽取出的结构化信息，利用图数据库进行知识融合与存储，形成一张互联的故障诊断知识网络，支
持高效查询与推理。
3、应用验证与系统实现
通过案例测试，评估知识获取流程的完整性与应用效果，证明其价值。

三附加要求：
  ❯ 注意低查重率和低AI感                                                               
  ❯ 注重理论深度的同时,也要有合理性,贴合我代码的实现                                                   
  ❯ 从多个维度 对论文进行系统性的提升，让它更像一份扎实且有深度的工程类学术研究成果，注重算法细节，不同垂直领域schema设计，Neo4j&Docker&MinIO&前后端的API串联等等 