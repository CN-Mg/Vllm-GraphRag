# experiments目录实验分析报告

## 概述

experiments目录包含了多个Jupyter Notebook文件，用于测试和验证知识图谱构建系统的不同方面。这些实验为系统的优化和部署提供了宝贵的数据支撑。

## 实验文件详情

### 1. **chunk_size_variable.ipynb**
**主要用途**：测试不同文档分块大小对知识图谱构建效果的影响

**实验内容**：
- 测试不同chunk size（200, 500, 1000, 2000, 5000 tokens）对知识图谱构建的影响
- 使用相同的PDF文档（"Apple stock during pandemic.pdf"）
- 统计不同分块策略下的：
  - 节点数量（nodes list vs distinct nodes）
  - 关系数量（relationships）
  - 处理效果差异

**实验发现**：
- chunk size 200：生成了28个节点（24个唯一节点），16个关系
- chunk size增大时，节点数量有变化但不是线性增长
- 需要平衡分块大小和上下文完整性

**实验目的**：找到最优的文档分块策略，平衡信息完整性和处理效率。

### 2. **multiple_models.ipynb**
**主要用途**：比较不同LLM模型在知识图谱构建上的表现

**测试的模型包括**：
- Microsoft Azure OpenAI GPT-4o
- Amazon Bedrock Claude
- Anthropic Claude 3.5 Sonnet
- Fireworks Llama
- Ollama（本地模型）

**实验发现**：
- **Azure OpenAI**：表现最好，能成功提取节点和关系，结构化输出完整
- **Amazon Bedrock**：无法生成有效的节点和关系，返回空结果
- **Anthropic Claude**：出现 AttributeError: 'Message' object has no attribute '__pydantic_serializer__'
- **Fireworks**：无法生成节点和关系，返回空结果
- **Ollama**：需要关闭node_properties功能才能工作，生成的基础图谱质量一般

**重要结论**：
```python
# Ollama的解决方案
llm_transformer = LLMGraphTransformer(llm=ollama_llm, node_properties=False)
```

### 3. **NER相关实验**
#### **NER_using_hugging_face_transformers_bert.ipynb**
- 测试BERT模型在PDF文档上的命名实体识别
- 使用dslim/bert-base-NER模型
- 测试4个PDF：
  - Harry Potter and the Death Hallows Summary.pdf
  - About Amazon.pdf
  - Apple stock during pandemic.pdf
  - Bank of America Q23.pdf

**实体类型**：
- O: Outside of a named entity
- B-MISC: Beginning of a miscellaneous entity
- I-MIS: Miscellaneous entity
- B-PER: Beginning of a person's name
- I-PER: Person's name
- B-ORG: Beginning of an organization
- I-ORG: organization
- B-LOC: Beginning of a location
- I-LOC: Location

#### **NER_using_spacy.ipynb**
- 使用spaCy进行命名实体识别实验
- 作为对比实验，评估传统NER方法的效果

**目的**：评估传统NER方法与LLM方法的效果对比。

### 4. **PDF转KG方案对比实验**
#### **PDF_to_KG_using_llamaindex.ipynb**
- 使用LlamaIndex框架进行PDF到知识图谱的转换
- 测试LlamaIndex在不同场景下的效果
- 对比LangChain方案的优势和不足

#### **PDF_to_kg_using_OpenAI.ipynb**
- 使用OpenAI API直接构建知识图谱
- 测试纯OpenAI方案的效果
- 评估直接API调用 vs LangChain封装的性能差异

#### **PDF_to_KG_using_Rebel.ipynb**
- 使用REBEL（关系提取）模型构建知识图谱
- REBEL是一个专门用于关系提取的开源模型
- 测试开源方案与闭源方案的差异

### 5. **Q_A_integration_using_RAGS (1).ipynb**
**主要用途**：测试RAG（检索增强生成）系统的集成效果

**实验内容**：
- 结合向量检索（Neo4jVector）和图查询（GraphCypherQAChain）
- 比较纯文本检索 vs 图查询的结果
- 混合两种结果生成最终答案

**关键发现**：
```python
# 纯文本检索结果
{
    'result': "Apple Inc. (AAPL) is a multinational technology company...",
    'source': ['Apple stock during pandemic.pdf']
}

# 图查询结果
{
    'query': 'What do you know about Suarez',
    'result': 'Suarez is a Uruguayan forward.'
}

# 混合策略效果更好
final_prompt = f"""You are a helpful question-answering agent. Your task is to analyze
and synthesize information from two sources: the top result from a similarity search
(unstructured information) and relevant data from a graph database (structured information)...
"""
```

### 6. **性能对比文件**
- **Combined chunks sequential and parallel execution comparision.ipynb**：比较串行和并行执行的效果
- **Combined chunk comparision.png**：可视化对比结果
- **LLM_Results_.csv**：实验结果数据表

### 7. **文档记录**
- **Experimentations for Kg creation.docx**：详细的实验记录文档
- **LLM Comparisons with one pdf.docx**：单个PDF的LLM对比结果

## 实验价值总结

### 1. **技术选型指导**
- 帮助选择最佳的LLM模型：Azure OpenAI表现最佳
- 确定最优的文档分块策略：需要根据具体场景调整
- 评估不同框架（LangChain vs LlamaIndex）的效果

### 2. **参数优化**
- 找到最佳的分块大小：实验显示不同大小各有优劣
- 测试不同模型的temperature参数：影响输出的创造性
- 优化检索相关的参数（k值、阈值等）

### 3. **问题定位**
- 识别系统瓶颈：LLM调用是主要瓶颈
- 发现模型兼容性问题：如Ollama需要特殊配置
- 理解不同场景下的适用方案：文本vs图片处理

### 4. **性能基准**
- 建立处理速度基准：为后续优化提供参考
- 评估内存使用情况：指导资源分配
- 比较不同硬件配置的效果：指导基础设施规划

### 5. **最佳实践总结**
1. **模型选择**：
   - 生产环境推荐使用Azure OpenAI
   - 本地部署可考虑Ollama（需调整配置）
   - 避免使用表现不佳的模型（如Bedrock）

2. **错误处理**：
   - 为每个模型配置回退策略
   - 使用try-catch包装LLM调用
   - 实现结果验证机制

3. **性能优化**：
   - 使用asyncio.to_thread处理阻塞操作
   - 批量处理文档和chunks
   - 合理设置并发数

## 实验建议

### 1. **后续实验方向**
- 测试更多开源模型（如LLaMA 2、Mistral）
- 评估不同embedding模型的效果
- 测试更大规模文档的处理能力

### 2. **生产环境部署建议**
- 基于实验结果选择合适的模型组合
- 建立性能监控和告警机制
- 实现自动化的容错和重试机制

### 3. **持续优化建议**
- 定期重新评估模型性能
- 根据实际使用情况调整参数
- 收集用户反馈持续改进

这些实验文件为项目的优化和部署提供了宝贵的数据支撑，帮助开发者避免踩坑，选择最合适的技术方案。