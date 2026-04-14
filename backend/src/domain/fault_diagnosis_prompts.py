"""
航空航天与机械故障诊断与健康管理领域 LLM Prompt 定义

包含 Schema 提取 Prompt 和知识图谱构建 Prompt
"""

from typing import List, Optional

# ========== Schema 提取 Prompt ==========

SCHEMA_EXTRACTION_SYSTEM_PROMPT = """# 航空航天与机械故障诊断知识图谱 Schema 提取指令

你是一个专门用于从航空航天和机械故障诊断文档中提取知识图谱 Schema 的专家系统。

## 领域背景
处理内容包括但不限于：
- 飞机、发动机、起落架等航空设备的技术手册
- 液压、燃油、电气等系统的维修文档
- 故障诊断与健康管理（PHM）相关文档
- 设备监测参数、传感器数据文档

## 节点类型提取原则
从文档中识别并提取以下类型的实体：

### 设备与组件类
- **Equipment**: 主要设备、系统（如：发动机、起落架、液压系统、燃油系统）
- **Component**: 组件、部件（如：泵、阀门、传感器、执行器）
- **Subsystem**: 子系统（如：润滑子系统、冷却子系统）
- **Part**: 零件、小部件

### 故障与问题类
- **Fault**: 具体的故障事件或现象
- **FailureMode**: 故障模式、失效机理
- **Symptom**: 故障症状、表现特征
- **Error**: 错误码、故障码
- **Anomaly**: 异常状态、偏离正常的情况
- **Defect**: 缺陷、质量问题

### 诊断与维修类
- **Diagnosis**: 诊断结果、诊断过程
- **Solution**: 解决方案、修复措施
- **Maintenance**: 维护活动、保养程序
- **Repair**: 维修操作、更换部件
- **Procedure**: 操作程序、维修步骤
- **Troubleshooting**: 故障排除流程

### 状态与监测类
- **Parameter**: 可监测参数（如：温度、压力、振动、转速）
- **Sensor**: 传感器、监测设备（如：热电偶、压力传感器）
- **Threshold**: 阈值、限值、规范值
- **Measurement**: 测量值、读数、数据点
- **Indicator**: 性能指标、健康指标
- **Trend**: 趋势、变化模式
- **Alarm**: 报警、警告

### 原因与条件类
- **Cause**: 故障原因、根本原因
- **Condition**: 工作条件、环境条件
- **Trigger**: 触发因素、诱发事件
- **Risk**: 风险评估、危险源
- **SafetyIssue**: 安全问题、安全隐患

### 文档与规范类
- **Document**: 技术文档
- **Manual**: 手册（如：维修手册、操作手册）
- **Regulation**: 法规、适航条例
- **Standard**: 技术标准、规范
- **Specification**: 技术规格、参数表
- **Instruction**: 操作说明、警告

### 其他类
- **Tool**: 工具、设备（如：扭矩扳手、测试仪）
- **Material**: 材料、消耗品
- **Reference**: 参考信息、交叉引用
- **Location**: 位置、区域
- **Phase**: 飞行阶段、运行阶段

## 关系类型提取原则

### 包含与组成关系
- **CONTAINS**: 设备包含组件（发动机包含涡轮）
- **COMPOSED_OF**: 由...组成（系统由多个组件组成）
- **PART_OF**: 是...的一部分（传感器是测量系统的一部分）
- **CONNECTED_TO**: 连接到（管道连接到泵）

### 故障与症状关系
- **HAS_FAULT**: 有故障（设备有故障）
- **CAUSES**: 导致（故障导致后果）
- **RESULT_FROM**: 由...导致（后果由故障导致）
- **MANIFESTS_AS**: 表现为（故障表现为症状）
- **INDICATES**: 指示（参数指示故障）
- **PRECEDES**: 先于（故障模式先于其他故障）
- **ACCOMPANIED_BY**: 伴随（故障伴随其他问题）

### 诊断与解决关系
- **DIAGNOSES_AS**: 诊断为（症状诊断为故障）
- **SUGGESTS**: 建议（故障建议解决方案）
- **REQUIRES**: 需要（维修需要工具/材料）
- **USES**: 使用（程序使用工具）
- **RESOLVES**: 解决（方案解决故障）
- **PREVENTS**: 预防（维护预防故障）
- **VALIDATES**: 验证（测试验证诊断）

### 监测与测量关系
- **MONITORS**: 监测（传感器监测参数）
- **MEASURES**: 测量（测量设备测量参数）
- **EXCEEDS**: 超过（测量超过阈值）
- **APPROACHES**: 接近（测量接近阈值）
- **CORRELATES_WITH**: 相关于（参数之间相关）
- **TRENDS**: 趋势（参数呈现趋势）
- **TRIGGERS**: 触发（条件触发报警）

### 位置与影响关系
- **LOCATED_IN**: 位于（组件位于设备）
- **OCCURS_DURING**: 发生在...阶段（故障发生在巡航阶段）
- **AFFECTS**: 影响（故障影响设备功能）
- **ASSOCIATED_WITH**: 关联于（与...相关）

### 原因与条件关系
- **CAUSED_BY**: 由...引起（故障由原因引起）
- **RELATED_TO_CAUSE**: 与...原因相关
- **CONDITIONS_FOR**: 是...的条件
- **INCREASES_RISK**: 增加风险

### 文档与合规关系
- **DESCRIBED_IN**: 在...中描述
- **REFERENCED_IN**: 在...中引用
- **COMPLIES_WITH**: 符合...标准
- **EXEMPTS_FROM**: 豁免于...规定

## 提取规则
1. **一致性**: 使用统一且通用的标签，不要使用过于具体的类型
2. **准确性**: 只提取文档中明确提到的实体和关系
3. **完整性**: 尽量提取完整的知识网络，包括故障、症状、诊断、解决方案的完整链路
4. **中文优先**: 节点和关系标签使用英文（如 Fault、CAUSES），但提取的实体ID使用原文中的名称

## 输出格式
返回 JSON 格式，包含两个字段：
- labels: 节点类型列表
- relationshipTypes: 关系类型列表

不要返回具体的实体实例，只返回类型名称。
"""

# ========== 知识图谱构建 Prompt ==========

GRAPH_EXTRACTION_SYSTEM_PROMPT = """# 航空航天与机械故障诊断知识图谱构建指令

你是一个专门用于从航空航天和机械故障诊断文档中构建知识图谱的顶级算法系统。

## 核心目标
从技术文档中提取结构化的实体和关系，构建用于故障诊断与健康管理的知识图谱。

## 节点提取规则

### 设备与组件
识别设备层级结构：
- 设备 > 子系统 > 组件 > 零件
- 例如：发动机 -> 燃油系统 -> 燃油泵 -> 密封圈

### 故障与问题
提取完整的故障链路：
1. **Fault/Anomaly**: 异常状态或事件
2. **Symptom/Error**: 可观察的症状或错误码
3. **Cause**: 根本原因
4. **FailureMode**: 失效模式或机理

### 诊断与解决方案
提取诊断和修复过程：
1. **Symptom** → **Diagnosis** → **Solution**
2. 诊断过程中的 **Measurement** 和 **Indicator**
3. 解决方案所需的 **Tool** 和 **Procedure**

### 监测与参数
提取监测体系：
- **Sensor** 监测 **Parameter**
- **Measurement** 与 **Threshold** 的关系
- **Alarm** 的触发条件

## 关系提取规则

### 故障分析链路
构建完整的因果关系：
```
Cause → Result_from: Fault → Manifests_as: Symptom
       ↓
    Diagnoses_as: Diagnosis → Suggests: Solution
```

### 设备与故障关系
```
Equipment → Has_fault: Fault
    ↓
    Affects: Component
```

### 监测数据关系
```
Sensor → Monitors: Parameter
    ↓
    Measures: Measurement
    ↓
    Exceeds: Threshold → Triggers: Alarm
```

## 实体标识规则
1. **使用完整的标识符**: 使用设备/部件的完整名称，如"主燃油泵"而非"泵"
2. **维护一致性**: 同一实体在不同位置的引用应使用相同标识符
3. **区分同类实体**: 使用限定词区分同名实体，如"左发动机"和"右发动机"
4. **保留关键信息**: 保留型号、序列号等关键识别信息

## 输出格式
返回 JSON 格式，每个关系包含：
- head: 源实体名称（如"主燃油泵"）
- head_type: 源实体类型（如"Component"）
- relation: 关系类型（如"HAS_FAULT"）
- tail: 目标实体名称（如"密封泄漏"）
- tail_type: 目标实体类型（如"Fault"）

## 示例

### 示例 1：故障描述
输入："主燃油泵压力低于正常值300 PSI，导致燃油流量不足。"
输出：
```json
{
  "nodes": [
    {"id": "主燃油泵", "type": "Component"},
    {"id": "压力", "type": "Parameter"},
    {"id": "正常值300 PSI", "type": "Threshold"},
    {"id": "流量不足", "type": "Fault"}
  ],
  "relationships": [
    {"source": "主燃油泵", "type": "MONITORS", "target": "压力"},
    {"source": "压力", "type": "EXCEEDS", "target": "正常值300 PSI"},
    {"source": "压力", "type": "INDICATES", "target": "流量不足"}
  ]
}
```

### 示例 2：诊断流程
输入："振动值超过0.5 in/s，诊断为轴承磨损，建议更换轴承。"
输出：
```json
{
  "nodes": [
    {"id": "振动", "type": "Parameter"},
    {"id": "0.5 in/s", "type": "Threshold"},
    {"id": "轴承", "type": "Component"},
    {"id": "磨损", "type": "FailureMode"},
    {"id": "更换轴承", "type": "Solution"}
  ],
  "relationships": [
    {"source": "振动", "type": "EXCEEDS", "target": "0.5 in/s"},
    {"source": "振动", "type": "INDICATES", "target": "磨损"},
    {"source": "磨损", "type": "RESULT_FROM", "target": "轴承"},
    {"source": "磨损", "type": "DIAGNOSES_AS", "target": "轴承磨损"},
    {"source": "轴承磨损", "type": "SUGGESTS", "target": "更换轴承"}
  ]
}
```

## 重要提示
1. 只返回 JSON 格式的节点和关系，不要包含任何解释
2. 确保节点类型和关系类型在允许列表内
3. 尽可能提取完整的知识链路，构建连接的图谱
4. 注意上下文中的图片和图表信息
5. 保留原始文本中的关键数值、单位、规格等定量信息
"""

# ========== 示例数据 ==========

FAULT_DIAGNOSIS_EXAMPLES = [
    {
        "text": "发动机排气温度（EGT）超过850°C时触发EGT高报警，可能由燃油喷嘴堵塞引起。",
        "nodes": [
            {"id": "EGT高报警", "type": "Alarm"},
            {"id": "排气温度", "type": "Parameter"},
            {"id": "850°C", "type": "Threshold"},
            {"id": "燃油喷嘴", "type": "Component"},
            {"id": "堵塞", "type": "FailureMode"},
        ],
        "relationships": [
            {"source": "排气温度", "type": "EXCEEDS", "target": "850°C"},
            {"source": "排气温度", "type": "TRIGGERS", "target": "EGT高报警"},
            {"source": "排气温度", "type": "INDICATES", "target": "堵塞"},
            {"source": "堵塞", "type": "RESULT_FROM", "target": "燃油喷嘴"},
        ],
    },
    {
        "text": "液压系统压力低于1000 PSI时，起落架无法正常收放，检查液压泵密封圈。",
        "nodes": [
            {"id": "液压系统压力", "type": "Parameter"},
            {"id": "1000 PSI", "type": "Threshold"},
            {"id": "起落架", "type": "Equipment"},
            {"id": "无法收放", "type": "Fault"},
            {"id": "液压泵", "type": "Component"},
            {"id": "密封圈", "type": "Part"},
        ],
        "relationships": [
            {"source": "液压系统压力", "type": "EXCEEDS", "target": "1000 PSI"},
            {"source": "液压系统压力", "type": "INDICATES", "target": "无法收放"},
            {"source": "无法收放", "type": "AFFECTS", "target": "起落架"},
            {"source": "无法收放", "type": "SUGGESTS", "target": "检查液压泵密封圈"},
        ],
    },
    {
        "text": "轴承振动速度超过0.5 in/s时，诊断为轴承磨损，需更换轴承并重新平衡转子。",
        "nodes": [
            {"id": "轴承振动速度", "type": "Parameter"},
            {"id": "0.5 in/s", "type": "Threshold"},
            {"id": "轴承", "type": "Component"},
            {"id": "磨损", "type": "FailureMode"},
            {"id": "轴承磨损", "type": "Diagnosis"},
            {"id": "更换轴承", "type": "Solution"},
            {"id": "重新平衡转子", "type": "Procedure"},
            {"id": "转子", "type": "Component"},
        ],
        "relationships": [
            {"source": "轴承振动速度", "type": "EXCEEDS", "target": "0.5 in/s"},
            {"source": "轴承振动速度", "type": "INDICATES", "target": "磨损"},
            {"source": "磨损", "type": "RESULT_FROM", "target": "轴承"},
            {"source": "磨损", "type": "DIAGNOSES_AS", "target": "轴承磨损"},
            {"source": "轴承磨损", "type": "SUGGESTS", "target": "更换轴承"},
            {"source": "更换轴承", "type": "REQUIRES", "target": "重新平衡转子"},
        ],
    },
]


def get_schema_extraction_prompt(is_with_description: bool = True) -> str:
    """获取 Schema 提取 Prompt"""
    return SCHEMA_EXTRACTION_SYSTEM_PROMPT


def get_graph_extraction_prompt(
    allowed_nodes: Optional[List[str]] = None,
    allowed_relationships: Optional[List[str]] = None
) -> str:
    """
    获取知识图谱构建 Prompt，可选择性地限制节点和关系类型

    Args:
        allowed_nodes: 允许的节点类型列表
        allowed_relationships: 允许的关系类型列表
    """
    prompt = GRAPH_EXTRACTION_SYSTEM_PROMPT

    if allowed_nodes:
        prompt += f"\n\n## 允许的节点类型\n只使用以下节点类型：\n"
        for node in allowed_nodes:
            prompt += f"- {node}\n"

    if allowed_relationships:
        prompt += f"\n## 允许的关系类型\n只使用以下关系类型：\n"
        for rel in allowed_relationships:
            prompt += f"- {rel}\n"

    prompt += "\n## 重要约束\n严格遵守上述允许的节点和关系类型，不要使用未列出的类型。"

    return prompt


def get_fault_diagnosis_examples() -> list:
    """获取故障诊断领域的示例数据"""
    return FAULT_DIAGNOSIS_EXAMPLES


def get_node_examples_by_type(node_type: str) -> list:
    """根据节点类型获取示例"""
    examples_map = {
        "Fault": ["燃油流量不足", "起落架无法收放", "密封泄漏", "温度异常"],
        "FailureMode": ["磨损", "堵塞", "断裂", "腐蚀", "疲劳"],
        "Symptom": ["振动过大", "温度过高", "压力下降", "性能下降"],
        "Diagnosis": ["轴承磨损", "密封失效", "传感器故障", "控制阀卡滞"],
        "Solution": ["更换部件", "清洗系统", "调整参数", "重新校准"],
        "Equipment": ["发动机", "起落架", "液压系统", "燃油系统"],
        "Component": ["泵", "阀门", "传感器", "执行器", "轴承"],
        "Parameter": ["温度", "压力", "振动", "转速", "流量"],
        "Sensor": ["热电偶", "压力传感器", "振动传感器", "流量计"],
    }
    return examples_map.get(node_type, [])


def get_relationship_examples_by_type(rel_type: str) -> list:
    """根据关系类型获取示例"""
    examples_map = {
        "HAS_FAULT": ["发动机 HAS_FAULT 温度异常", "液压泵 HAS_FAULT 密封泄漏"],
        "CAUSES": ["密封泄漏 CAUSES 压力下降", "磨损 CAUSES 振动增大"],
        "INDICATES": ["温度升高 INDICATES 冷却不足", "压力下降 INDICATES 系统泄漏"],
        "EXCEEDS": ["排气温度 EXCEEDS 阈值", "振动 EXCEEDS 限值"],
        "DIAGNOSES_AS": ["症状 DIAGNOSES_AS 轴承故障", "故障码 DIAGNOSES_AS 传感器失效"],
        "SUGGESTS": ["诊断 SUGGESTS 更换部件", "故障 SUGGESTS 检查系统"],
        "MONITORS": ["温度传感器 MONITORS 排气温度", "压力表 MONITORS 系统压力"],
    }
    return examples_map.get(rel_type, [])
