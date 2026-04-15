# 知识图谱构建平台 - 航空航天机械故障诊断

## 项目概述

这是一个专门为航空航天机械故障诊断与健康管理（PHM）领域设计的知识图谱构建平台。该平台能够将非结构化的技术文档、维修手册、故障报告等数据，通过大语言模型（LLM）转换为结构化的知识图谱，存储在Neo4j数据库中，支持智能查询、可视化和诊断分析。

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
- **Web页面**: 支持URL直接导入
- **API接口**: 提供RESTful API供外部系统集成

### 6. 智能查询与交互
- **向量检索**: 基于语义相似度的文档检索
- **图谱查询**: 基于知识图谱的结构化查询
- **混合模式**: 结合向量检索和图谱查询的混合模式
- **图像分析**: 支持图像内容的智能问答

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (Frontend)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  文件上传   │  │  知识图谱   │  │  智能问答   │  │
│  │  组件       │  │  可视化     │  │  系统       │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   后端 (Backend)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   LLM      │  │   图谱      │  │   存储      │  │
│  │   接口     │  │   处理      │  │   管理      │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ GLM-4/4.6v │  │ 故障诊断   │  │   MinIO     │  │
│  │ DeepSeek   │  │   Schema    │  │   对象存储   │  │
│  │ Qwen       │  │             │  │             │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   数据库 (Database)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  Neo4j     │  │   MinIO     │  │   日志      │  │
│  │  知识图谱   │  │   图像存储   │  │   系统      │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
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
| GLM | glm-4 | 通用文本处理 |
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

## 🎯 项目路线图

- [√] 基础知识图谱构建
- [√] 多LLM模型集成
- [√] 图像解析功能
- [√] 故障诊断Schema
- [√] MinIO集成
- [√] 高级可视化功能
- [ ] 移动端支持
- [ ] 多语言支持
- [ ] 性能优化
- [ ] 企业级功能

---

**BUAA_7** 🚀