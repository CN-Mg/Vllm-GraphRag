"""
Schema 提取模块 - 支持通用和故障诊断领域
"""
from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field
from src.llm import get_llm
from src.shared.constants import MODEL_VERSIONS
from langchain_core.prompts import ChatPromptTemplate
from src.domain.fault_diagnosis_prompts import (
    get_schema_extraction_prompt as get_fault_diagnosis_schema_prompt,
    get_fault_diagnosis_examples,
)

class Schema(BaseModel):
    """Knowledge Graph Schema."""

    labels: List[str] = Field(description="list of node labels or types in a graph schema")
    relationshipTypes: List[str] = Field(description="list of relationship types in a graph schema")


# 通用 Prompt（原保留）
PROMPT_TEMPLATE_GENERAL = (
    "You are an expert in schema extraction, especially for extracting graph schema information from various formats."
    "Generate a generalized graph schema based on input text. Identify key entities and their relationships and "
    "provide a generalized label for the overall context"
    "Schema representations formats can contain extra symbols, quotes, or comments. Ignore all that extra markup."
    "Only return string types for nodes and relationships. Don't return attributes."
)

PROMPT_TEMPLATE_GENERAL_WITHOUT_SCHEMA = (
    "You are an expert in schema extraction, especially for deriving graph schema information from example texts."
    "Analyze the following text and extract only the types of entities and relationships from example prose."
    "Don't return any actual entities like people's names or instances of organizations."
    "Only return string types for nodes and relationships, don't return attributes."
)


def schema_extraction_from_text(input_text: str, model: str, is_schema_description_checked: bool, use_fault_diagnosis_domain: bool = True):
    """
    从文本中提取 Schema

    Args:
        input_text: 输入文本
        model: 使用的 LLM 模型
        is_schema_description_checked: 是否使用带描述的 Prompt
        use_fault_diagnosis_domain: 是否使用故障诊断领域的 Prompt（默认 True）

    Returns:
        Schema 对象，包含节点类型和关系类型
    """
    llm, model_name = get_llm(model)

    # 根据领域选择 Prompt
    if use_fault_diagnosis_domain:
        schema_prompt = get_fault_diagnosis_schema_prompt(is_schema_description_checked)
    else:
        if is_schema_description_checked:
            schema_prompt = PROMPT_TEMPLATE_GENERAL
        else:
            schema_prompt = PROMPT_TEMPLATE_GENERAL_WITHOUT_SCHEMA

    prompt = ChatPromptTemplate.from_messages(
        [("system", schema_prompt), ("user", "{text}")]
    )

    runnable = prompt | llm.with_structured_output(
        schema=Schema,
        method="function_calling",
        include_raw=False,
    )

    raw_schema = runnable.invoke({"text": input_text})
    return raw_schema


def get_domain_examples() -> List[dict]:
    """
    获取故障诊断领域的示例数据（用于调试或测试）

    Returns:
        示例数据列表
    """
    return get_fault_diagnosis_examples()


def get_available_domains() -> dict:
    """
    获取可用的领域配置

    Returns:
        领域配置字典
    """
    return {
        "fault_diagnosis": {
            "name": "航空航天与机械故障诊断",
            "description": "适用于飞机、发动机、液压系统等航空设备的技术手册和故障诊断文档",
            "enabled": True,
        },
        "general": {
            "name": "通用领域",
            "description": "适用于各种类型的文本内容，提取通用的实体和关系",
            "enabled": True,
        },
    }


def get_schema_for_domain(domain_name: str) -> dict:
    """
    获取指定领域的完整 Schema 定义

    Args:
        domain_name: 领域名称（如 "fault_diagnosis"）

    Returns:
        Schema 定义字典
    """
    domains = get_available_domains()

    if domain_name == "fault_diagnosis":
        from src.domain.fault_diagnosis_schema import get_schema_for_export
        return {
            "name": domains[domain_name]["name"],
            "description": domains[domain_name]["description"],
            "schema": get_schema_for_export(),
        }
    else:
        return {
            "name": domains[domain_name]["name"],
            "description": domains[domain_name]["description"],
            "schema": {
                "nodes": {},
                "relationships": {},
                "defaults": {
                    "allowed_nodes": [],
                    "allowed_relationships": [],
                },
            },
        }
