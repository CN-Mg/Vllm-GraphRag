# -*- coding: utf-8 -*-
"""
知识图谱转换器 - 支持通用和故障诊断领域
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union, cast

from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain_core.pydantic_v1 import BaseModel, Field, create_model

# 故障诊断领域示例
FAULT_DIAGNOSIS_EXAMPLES = [
    {
        "text": "发动机排气温度（EGT）超过850°C时触发EGT高报警，可能由燃油喷嘴堵塞引起。",
        "head": "排气温度",
        "head_type": "Parameter",
        "relation": "EXCEEDS",
        "tail": "850°C",
        "tail_type": "Threshold",
    },
    {
        "text": "排气温度超过850°C触发EGT高报警，可能由燃油喷嘴堵塞引起。",
        "head": "排气温度",
        "head_type": "Parameter",
        "relation": "TRIGGERS",
        "tail": "EGT高报警",
        "tail_type": "Alarm",
    },
    {
        "text": "EGT高报警指示燃油喷嘴堵塞。",
        "head": "EGT高报警",
        "head_type": "Alarm",
        "relation": "INDICATES",
        "tail": "堵塞",
        "tail_type": "FailureMode",
    },
    {
        "text": "堵塞导致燃油喷嘴故障。",
        "head": "堵塞",
        "head_type": "FailureMode",
        "relation": "RESULT_FROM",
        "tail": "燃油喷嘴",
        "tail_type": "Component",
    },
    {
        "text": "液压系统压力低于1000 PSI时，起落架无法正常收放。",
        "head": "液压系统压力",
        "head_type": "Parameter",
        "relation": "EXCEEDS",
        "tail": "1000 PSI",
        "tail_type": "Threshold",
    },
    {
        "text": "液压系统压力下降指示起落架无法收放。",
        "head": "液压系统压力",
        "head_type": "Parameter",
        "relation": "INDICATES",
        "tail": "无法收放",
        "tail_type": "Fault",
    },
    {
        "text": "无法收放影响起落架功能。",
        "head": "无法收放",
        "head_type": "Fault",
        "relation": "AFFECTS",
        "tail": "起落架",
        "tail_type": "Equipment",
    },
    {
        "text": "起落架故障建议检查液压泵密封圈。",
        "head": "起落架故障",
        "head_type": "Fault",
        "relation": "SUGGESTS",
        "tail": "检查液压泵密封圈",
        "tail_type": "Solution",
    },
    {
        "text": "轴承振动超过0.5 in/s时诊断为轴承磨损。",
        "head": "轴承振动",
        "head_type": "Parameter",
        "relation": "EXCEEDS",
        "tail": "0.5 in/s",
        "tail_type": "Threshold",
    },
    {
        "text": "振动超过限值指示轴承磨损。",
        "head": "振动",
        "head_type": "Parameter",
        "relation": "INDICATES",
        "tail": "磨损",
        "tail_type": "FailureMode",
    },
    {
        "text": "磨损导致轴承故障。",
        "head": "磨损",
        "head_type": "FailureMode",
        "relation": "RESULT_FROM",
        "tail": "轴承",
        "tail_type": "Component",
    },
    {
        "text": "振动和磨损诊断为轴承磨损。",
        "head": "振动异常",
        "head_type": "Symptom",
        "relation": "DIAGNOSES_AS",
        "tail": "轴承磨损",
        "tail_type": "Diagnosis",
    },
    {
        "text": "轴承磨损建议更换轴承。",
        "head": "轴承磨损",
        "head_type": "Diagnosis",
        "relation": "SUGGESTS",
        "tail": "更换轴承",
        "tail_type": "Solution",
    },
]

# 通用示例（保留原示例）
GENERAL_EXAMPLES = [
    {
        "text": "Adam is a software engineer in Microsoft since 2009, and last year he got an award as the Best Talent",
        "head": "Adam",
        "head_type": "Person",
        "relation": "WORKS_FOR",
        "tail": "Microsoft",
        "tail_type": "Company",
    },
    {
        "text": "Adam is a software engineer in Microsoft since 2009, and last year he got an award as the Best Talent",
        "head": "Adam",
        "head_type": "Person",
        "relation": "HAS_AWARD",
        "tail": "Best Talent",
        "tail_type": "Award",
    },
]

# 故障诊断领域 System Prompt
FAULT_DIAGNOSIS_SYSTEM_PROMPT = """# 航空航天与机械故障诊断知识图谱构建指令

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
4. **保留关键信息**: 保留型号、序列号、数值、单位等关键识别信息

## 输出格式
返回 JSON 格式，每个关系包含：
- head: 源实体名称（如"主燃油泵"）
- head_type: 源实体类型（如"Component"）
- relation: 关系类型（如"HAS_FAULT"）
- tail: 目标实体名称（如"密封泄漏"）
- tail_type: 目标实体类型（如"Fault"）

## 重要提示
1. 只返回 JSON 格式的节点和关系，不要包含任何解释
2. 确保节点类型和关系类型在允许列表内
3. 尽可能提取完整的知识链路，构建连接的图谱
4. 注意上下文中的图片和图表信息
5. 保留原始文本中的关键数值、单位、规格等定量信息
"""

# 通用 System Prompt（保留）
GENERAL_SYSTEM_PROMPT = (
    "# Knowledge Graph Instructions for GPT-4\n"
    "## 1. Overview\n"
    "You are a top-tier algorithm designed for extracting information in structured "
    "formats to build a knowledge graph.\n"
    "Try to capture as much information from the text as possible without "
    "sacrifing accuracy. Do not add any information that is not explicitly "
    "mentioned in the text\n"
    "- **Nodes** represent entities and concepts.\n"
    "- The aim is to achieve simplicity and clarity in the knowledge graph, making it\n"
    "accessible for a vast audience.\n"
    "## 2. Labeling Nodes\n"
    "- **Consistency**: Ensure you use available types for node labels.\n"
    "Ensure you use basic or elementary types for node labels.\n"
    "- For example, when you identify an entity representing a person, "
    "always label it as **'Person'**. Avoid using more specific terms "
    "like 'mathematician' or 'scientist'\n"
    "  - **Node IDs**: Never utilize integers as node IDs. Node IDs should be "
    "names or human-readable identifiers found in the text.\n"
    "- **Relationships** represent connections between entities or concepts.\n"
    "Ensure consistency and generality in relationship types when constructing "
    "knowledge graphs. Instead of using specific and momentary types "
    "such as 'BECAME_PROFESSOR', use more general and timeless relationship types "
    "like 'PROFESSOR'. Make sure to use general and timeless relationship types!\n"
    "## 3. Coreference Resolution\n"
    "- **Maintain Entity Consistency**: When extracting entities, it's vital to "
    "ensure consistency.\n"
    'If an entity, such as "John Doe", is mentioned multiple times in the text '
    'but is referred to by different names or pronouns (e.g., "Joe", "he"),'
    "always use the most complete identifier for that entity throughout the "
    'knowledge graph. In this example, use "John Doe" as the entity ID.\n'
    "Remember that the knowledge graph should be coherent and easily understandable, "
    "so maintaining consistency in entity references is crucial.\n"
    "## 4. Strict Compliance\n"
    "Adhere to the rules strictly. Non-compliance will result in termination."
)


def _get_additional_info(input_type: str, use_fault_diagnosis_domain: bool = True) -> str:
    """获取节点/关系类型的额外说明"""
    if input_type not in ["node", "relationship", "property"]:
        raise ValueError("input_type must be 'node', 'relationship', or 'property'")

    if use_fault_diagnosis_domain:
        # 故障诊断领域的说明
        if input_type == "node":
            return (
                "确保使用故障诊断领域的节点类型，如：Equipment、Component、Fault、Symptom、"
                "Diagnosis、Solution、Parameter、Sensor、Threshold 等。"
                "使用完整且具体的设备/部件名称作为节点标识符。"
            )
        elif input_type == "relationship":
            return (
                "确保使用故障诊断领域的关系类型，如：HAS_FAULT、CAUSES、INDICATES、"
                "EXCEEDS、DIAGNOSES_AS、SUGGESTS、MONITORS、MEASURES 等。"
                "使用通用且无时态的关系类型。"
            )
    else:
        # 通用领域的说明
        if input_type == "node":
            return (
                "Ensure you use basic or elementary types for node labels.\n"
                "For example, when you identify an entity representing a person, "
                "always label it as **'Person'**. Avoid using more specific terms "
                "like 'Mathematician' or 'Scientist'"
            )
        elif input_type == "relationship":
            return (
                "Instead of using specific and momentary types such as "
                "'BECAME_PROFESSOR', use more general and timeless relationship types like "
                "'PROFESSOR'. However, do not sacrifice any accuracy for generality"
            )
    return ""


def optional_enum_field(
    enum_values: Optional[List[str]] = None,
    description: str = "",
    input_type: str = "node",
    use_fault_diagnosis_domain: bool = True,
    **field_kwargs: Any,
) -> Any:
    """条件性创建带枚举约束的字段"""
    if enum_values:
        return Field(
            ...,
            enum=enum_values,
            description=f"{description}. Available options are {enum_values}",
            **field_kwargs,
        )
    else:
        additional_info = _get_additional_info(input_type, use_fault_diagnosis_domain)
        return Field(..., description=description + additional_info, **field_kwargs)


class _Graph(BaseModel):
    nodes: Optional[List]
    relationships: Optional[List]


class UnstructuredRelation(BaseModel):
    head: str = Field(
        description=(
            "extracted head entity. "
            "Must use human-readable unique identifier."
        )
    )
    head_type: str = Field(
        description="type of the extracted head entity"
    )
    relation: str = Field(description="relation between head and tail entities")
    tail: str = Field(
        description=(
            "extracted tail entity. "
            "Must use human-readable unique identifier."
        )
    )
    tail_type: str = Field(
        description="type of the extracted tail entity"
    )


def create_unstructured_prompt(
    node_labels: Optional[List[str]] = None,
    rel_types: Optional[List[str]] = None,
    use_fault_diagnosis_domain: bool = True,
) -> ChatPromptTemplate:
    """创建非结构化 Prompt"""
    node_labels_str = str(node_labels) if node_labels else ""
    rel_types_str = str(rel_types) if rel_types else ""

    # 根据领域选择不同的 Prompt 内容
    if use_fault_diagnosis_domain:
        # 故障诊断领域 Prompt
        examples_str = json.dumps(FAULT_DIAGNOSIS_EXAMPLES, ensure_ascii=False, indent=2)

        base_string_parts = [
            "你是专门用于从航空航天和机械故障诊断文档中构建知识图谱的专家系统。",
            "你的任务是从给定文本中识别并提取故障诊断相关的实体和关系。",
            "必须以包含 JSON 对象列表的 JSON 格式生成输出。",
            "每个对象应包含 'head', 'head_type', 'relation', 'tail', 和 'tail_type' 键。",
        ]

        if node_labels:
            base_string_parts.append(
                f"'head_type' 键必须包含源实体类型，必须是以下类型之一：{node_labels_str}。"
            )

        if rel_types:
            base_string_parts.append(
                f"'relation' 键必须包含 'head' 和 'tail' 之间的关系类型，"
                f"必须是以下类型之一：{rel_types_str}。"
            )

        base_string_parts.append(
            f"'tail_type' 键必须表示关系尾部的实体类型，"
            f"必须是以下类型之一：{node_labels_str}。"
        )

        base_string_parts.append(
            "提取尽可能多的实体和关系。维护实体一致性："
            "当提取实体时，确保一致性。如果一个实体（如'主燃油泵'）"
            "在文本中多次被提及，但被不同的名称或代词引用，"
            "始终使用该实体最完整的标识符。"
        )

        base_string_parts.extend([
            "重要说明：",
            "- 不要添加任何解释和额外文本。",
            "- 只提取文档中明确提到的实体和关系。",
            "- 保留关键数值、单位、规格等定量信息。",
            "- 构建完整的故障-症状-诊断-解决方案链路。",
        ])

        system_prompt = "\n".join(filter(None, base_string_parts))

    else:
        # 通用领域 Prompt（原通用逻辑）
        base_string_parts = [
            "You are a top-tier algorithm designed for extracting information in "
            "structured formats to build a knowledge graph. Your task is to identify "
            "the entities and relations requested with user prompt from a given "
            "text. You must generate the output in a JSON format containing a list "
            'with JSON objects. Each object should have the keys: "head", '
            '"head_type", "relation", "tail", and "tail_type". The "head" '
            'key must contain the text of the extracted entity with one of the types '
            f"from the provided list in the user prompt.",
            f'The "head_type" key must contain the type of the extracted head entity, '
            f"which must be one of the types from {node_labels_str}."
            if node_labels
            else "",
            f'The "relation" key must contain the type of relation between "head" '
            f'and "tail", which must be one of the relations from {rel_types_str}.'
            if rel_types
            else "",
            f'The "tail" key must represent the text of an entity which is '
            f'the tail of the relation, and the "tail_type" key must contain the type '
            f"of the tail entity from {node_labels_str}."
            if node_labels
            else "",
            "Attempt to extract as many entities and relations as you can. Maintain "
            "Entity Consistency: When extracting entities, it's vital to ensure "
            'consistency. If an entity, such as "John Doe", is mentioned multiple '
            'times in the text but is referred to by different names or pronouns '
            '(e.g., "Joe", "he"), always use the most complete identifier for '
            "that entity. The knowledge graph should be coherent and easily "
            "understandable, so maintaining consistency in entity references is "
            "crucial.",
            "IMPORTANT NOTES:\n- Don't add any explanation and text.",
        ]

        system_prompt = "\n".join(filter(None, base_string_parts))

    system_message = SystemMessage(content=system_prompt)
    parser = JsonOutputParser(pydantic_object=UnstructuredRelation)

    examples = FAULT_DIAGNOSIS_EXAMPLES if use_fault_diagnosis_domain else GENERAL_EXAMPLES
    examples_str = json.dumps(examples, ensure_ascii=False, indent=2)

    human_prompt = PromptTemplate(
        template="""Based on the following example, extract entities and relations from the provided text.\n
Use the following entity types, don't use any entity that is not defined below:
# ENTITY TYPES:
{node_labels}

Use the following relation types, don't use any relation that is not defined below:
# RELATION TYPES:
{rel_types}

Below are a number of examples of text and their extracted entities and relationships.
{examples}

For the following text, extract entities and relations as in the provided example.
{format_instructions}
Text: {input}""",
        input_variables=["input"],
        partial_variables={
            "format_instructions": parser.get_format_instructions(),
            "node_labels": node_labels,
            "rel_types": rel_types,
            "examples": examples_str,
        },
    )

    human_message_prompt = HumanMessagePromptTemplate(prompt=human_prompt)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message, human_message_prompt]
    )
    return chat_prompt


def create_simple_model(
    node_labels: Optional[List[str]] = None,
    rel_types: Optional[List[str]] = None,
    node_properties: Union[bool, List[str]] = False,
    use_fault_diagnosis_domain: bool = True,
) -> Type[_Graph]:
    """
    创建简单模型，限制节点和/或关系类型
    不包含任何节点或关系属性。
    """
    node_fields: Dict[str, Tuple[Any, Any]] = {
        "id": (
            str,
            Field(..., description="Name or human-readable unique identifier."),
        ),
        "type": (
            str,
            optional_enum_field(
                node_labels,
                description="The type or label of node.",
                input_type="node",
                use_fault_diagnosis_domain=use_fault_diagnosis_domain,
            ),
        ),
    }

    if node_properties:
        if isinstance(node_properties, list) and "id" in node_properties:
            raise ValueError("The node property 'id' is reserved and cannot be used.")
        # Map True to empty array
        node_properties_mapped: List[str] = (
            [] if node_properties is True else node_properties
        )

        class Property(BaseModel):
            """A single property consisting of key and value"""
            key: str = optional_enum_field(
                node_properties_mapped,
                description="Property key.",
                input_type="property",
            )
            value: str = Field(..., description="value")

        node_fields["properties"] = (
            Optional[List[Property]],
            Field(None, description="List of node properties"),
        )

    SimpleNode = create_model("SimpleNode", **node_fields)

    class SimpleRelationship(BaseModel):
        """Represents a directed relationship between two nodes in a graph."""
        source_node_id: str = Field(
            description="Name or human-readable unique identifier of source node"
        )
        source_node_type: str = optional_enum_field(
            node_labels,
            description="The type or label of source node.",
            input_type="node",
            use_fault_diagnosis_domain=use_fault_diagnosis_domain,
        )
        target_node_id: str = Field(
            description="Name or human-readable unique identifier of target node"
        )
        target_node_type: str = optional_enum_field(
            node_labels,
            description="The type or label of target node.",
            input_type="node",
            use_fault_diagnosis_domain=use_fault_diagnosis_domain,
        )
        type: str = optional_enum_field(
            rel_types,
            description="The type of the relationship.",
            input_type="relationship",
            use_fault_diagnosis_domain=use_fault_diagnosis_domain,
        )

    class DynamicGraph(_Graph):
        """Represents a graph document consisting of nodes and relationships."""
        nodes: Optional[List[SimpleNode]] = Field(description="List of nodes")
        relationships: Optional[List[SimpleRelationship]] = Field(
            description="List of relationships"
        )

    return DynamicGraph


def map_to_base_node(node: Any) -> Node:
    """Map SimpleNode to base Node."""
    properties = {}
    if hasattr(node, "properties") and node.properties:
        for p in node.properties:
            properties[format_property_key(p.key)] = p.value
    return Node(id=node.id, type=node.type, properties=properties)


def map_to_base_relationship(rel: Any) -> Relationship:
    """Map SimpleRelationship to base Relationship."""
    source = Node(id=rel.source_node_id, type=rel.source_node_type)
    target = Node(id=rel.target_node_id, type=rel.target_node_type)
    return Relationship(source=source, target=target, type=rel.type)


def _parse_and_clean_json(
    argument_json: Dict[str, Any],
) -> Tuple[List[Node], List[Relationship]]:
    """解析和清洗 JSON 数据"""
    if 'Items' in argument_json["nodes"]:
        argument_json["nodes"] = argument_json['nodes']['Items']
    if 'Items' in argument_json["relationships"]:
        argument_json["relationships"] = argument_json["relationships"]['Items']

    nodes = []
    for node in argument_json["nodes"]:
        if not node.get("id"):
            continue
        nodes.append(
            Node(
                id=node["id"],
                type=node.get("type"),
            )
        )

    relationships = []
    for rel in argument_json["relationships"]:
        if (
            not rel.get("source_node_id")
            or not rel.get("target_node_id")
            or not rel.get("type")
        ):
            continue

        if not rel.get("source_node_type"):
            try:
                rel["source_node_type"] = [
                    el.get("type")
                    for el in argument_json["nodes"]
                    if el["id"] == rel["source_node_id"]
                ][0]
            except IndexError:
                rel["source_node_type"] = None

        if not rel.get("target_node_type"):
            try:
                rel["target_node_type"] = [
                    el.get("type")
                    for el in argument_json["nodes"]
                    if el["id"] == rel["target_node_id"]
                ][0]
            except IndexError:
                rel["target_node_type"] = None

        source_node = Node(
            id=rel["source_node_id"],
            type=rel["source_node_type"],
        )
        target_node = Node(
            id=rel["target_node_id"],
            type=rel["target_node_type"],
        )
        relationships.append(
            Relationship(
                source=source_node,
                target=target_node,
                type=rel["type"],
            )
        )

    return nodes, relationships


def _format_nodes(nodes: List[Node]) -> List[Node]:
    return [
        Node(
            id=el.id.title() if isinstance(el.id, str) else el.id,
            type=el.type.capitalize(),
            properties=el.properties,
        )
        for el in nodes
    ]


def _format_relationships(rels: List[Relationship]) -> List[Relationship]:
    return [
        Relationship(
            source=_format_nodes([el.source])[0],
            target=_format_nodes([el.target])[0],
            type=el.type.replace(" ", "_").upper(),
        )
        for el in rels
    ]


def format_property_key(s: str) -> str:
    words = s.split()
    if not words:
        return s
    first_word = words[0].lower()
    capitalized_words = [word.capitalize() for word in words[1:]]
    return "".join([first_word] + capitalized_words)


def _convert_to_graph_document(
    raw_schema: Dict[Any, Any],
) -> Tuple[List[Node], List[Relationship]]:
    """转换原始 schema 为图文档"""
    if not raw_schema["parsed"]:
        try:
            try:
                argument_json = json.loads(
                    raw_schema["raw"].additional_kwargs["tool_calls"][0]["function"][
                        "arguments"
                    ]
                )
            except Exception:
                argument_json = json.loads(
                    raw_schema["raw"].additional_kwargs["function_call"]["arguments"]
                )
            nodes, relationships = _parse_and_clean_json(argument_json)
        except Exception:
            return ([], [])
    else:
        parsed_schema: _Graph = raw_schema["parsed"]
        nodes = (
            [map_to_base_node(node) for node in parsed_schema.nodes]
            if parsed_schema.nodes
            else []
        )

        relationships = (
            [map_to_base_relationship(rel) for rel in parsed_schema.relationships]
            if parsed_schema.relationships
            else []
        )

    return _format_nodes(nodes), _format_relationships(relationships)


class LLMGraphTransformer:
    """使用 LLM 将文档转换为基于Graph的文档的转换器"""

    def __init__(
        self,
        llm: BaseLanguageModel,
        allowed_nodes: List[str] = [],
        allowed_relationships: List[str] = [],
        prompt: Optional[ChatPromptTemplate] = None,
        strict_mode: bool = True,
        node_properties: Union[bool, List[str]] = False,
        use_function_call: bool = True,
        use_fault_diagnosis_domain: bool = True,
    ) -> None:
        self.allowed_nodes = allowed_nodes
        self.allowed_relationships = allowed_relationships
        self.strict_mode = strict_mode
        self._function_call = use_function_call
        self.use_fault_diagnosis_domain = use_fault_diagnosis_domain

        # 检查模型是否支持函数调用
        try:
            llm.with_structured_output(_Graph)
        except NotImplementedError:
            self._function_call = False

        if not self._function_call:
            if node_properties:
                raise ValueError(
                    "The 'node_properties' parameter cannot be used "
                    "in combination with a LLM that doesn't support "
                    "native function calling."
                )
            try:
                import json_repair
                self.json_repair = json_repair
            except ImportError:
                raise ImportError(
                    "Could not import json_repair python package. "
                    "Please install it with `pip install json-repair`."
                )
            prompt = prompt or create_unstructured_prompt(
                allowed_nodes, allowed_relationships, use_fault_diagnosis_domain
            )
            self.chain = prompt | llm
        else:
            schema = create_simple_model(
                allowed_nodes, allowed_relationships, node_properties, use_fault_diagnosis_domain
            )
            structured_llm = llm.with_structured_output(schema, include_raw=True)

            # 根据领域选择 Prompt
            if use_fault_diagnosis_domain:
                prompt = prompt or ChatPromptTemplate.from_messages(
                    [
                        ("system", FAULT_DIAGNOSIS_SYSTEM_PROMPT),
                        (
                            "human",
                            (
                                "Tip: Make sure to answer in the correct format and do "
                                "not include any explanations. "
                                "Use the given format to extract information from the "
                                "following input: {input}"
                            ),
                        ),
                    ]
                )
            else:
                prompt = prompt or ChatPromptTemplate.from_messages(
                    [
                        ("system", GENERAL_SYSTEM_PROMPT),
                        (
                            "human",
                            (
                                "Tip: Make sure to answer in the correct format and do "
                                "not include any explanations. "
                                "Use the given format to extract information from the "
                                "following input: {input}"
                            ),
                        ),
                    ]
                )

            self.chain = prompt | structured_llm

    def process_response(self, document: Document) -> GraphDocument:
        """
        处理单个文档，使用 LLM 将其转换为Graph文档
        """
        text = document.page_content
        raw_schema = self.chain.invoke({"input": text})

        if self._function_call:
            raw_schema = cast(Dict[Any, Any], raw_schema)
            nodes, relationships = _convert_to_graph_document(raw_schema)
        else:
            nodes_set = set()
            relationships = []
            parsed_json = self.json_repair.loads(raw_schema.content)

            for rel in parsed_json:
                nodes_set.add((rel["head"], rel["head_type"]))
                nodes_set.add((rel["tail"], rel["tail_type"]))

                source_node = Node(id=rel["head"], type=rel["head_type"])
                target_node = Node(id=rel["tail"], type=rel["tail_type"])
                relationships.append(
                    Relationship(
                        source=source_node, target=target_node, type=rel["relation"]
                    )
                )

            nodes = [Node(id=el[0], type=el[1]) for el in list(nodes_set)]

        # 严格模式过滤
        if self.strict_mode and (self.allowed_nodes or self.allowed_relationships):
            if self.allowed_nodes:
                lower_allowed_nodes = [el.lower() for el in self.allowed_nodes]
                nodes = [
                    node for node in nodes if node.type.lower() in lower_allowed_nodes
                ]
                relationships = [
                    rel
                    for rel in relationships
                    if rel.source.type.lower() in lower_allowed_nodes
                    and rel.target.type.lower() in lower_allowed_nodes
                ]

            if self.allowed_relationships:
                relationships = [
                    rel
                    for rel in relationships
                    if rel.type.lower()
                    in [el.lower() for el in self.allowed_relationships]
                ]

        return GraphDocument(nodes=nodes, relationships=relationships, source=document)

    def convert_to_graph_documents(
        self, documents: Sequence[Document]
    ) -> List[GraphDocument]:
        """将一系列文档转换为图文档"""
        return [self.process_response(document) for document in documents]
