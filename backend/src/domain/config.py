"""
领域配置管理模块

提供不同领域的配置选项和默认值
"""
import os
from typing import Dict, List


# ========== 领域定义 ==========

DOMAINS = {
    "fault_diagnosis": {
        "name": "航空航天与机械故障诊断",
        "name_en": "Aerospace and Mechanical Fault Diagnosis",
        "description": "适用于飞机、发动机、液压系统等航空设备的技术手册和故障诊断文档",
        "schema_module": "src.domain.fault_diagnosis_schema",
        "prompts_module": "src.domain.fault_diagnosis_prompts",
        "enabled": True,
    },
    "general": {
        "name": "通用领域",
        "name_en": "General Purpose",
        "description": "适用于各种类型的文本内容，提取通用的实体和关系",
        "schema_module": None,
        "prompts_module": None,
        "enabled": True,
    },
}


# ========== 配置类 ==========


class DomainConfig:
    """领域配置类"""

    def __init__(self, domain_name: str = None):
        """
        Args:
            domain_name: 领域名称（如 "fault_diagnosis"）
                           如果为 None，则从环境变量读取
        """
        self.domain_name = domain_name or os.getenv("FAULT_DIAGNOSIS_DOMAIN", "fault_diagnosis")

    @property
    def is_fault_diagnosis(self) -> bool:
        """是否使用故障诊断领域"""
        return self.domain_name == "fault_diagnosis"

    @property
    def domain_info(self) -> Dict:
        """获取当前领域的详细信息"""
        return DOMAINS.get(self.domain_name, {})

    @property
    def default_allowed_nodes(self) -> List[str]:
        """获取默认允许的节点类型"""
        if self.is_fault_diagnosis:
            from src.domain.fault_diagnosis_schema import DEFAULT_ALLOWED_NODES
            return DEFAULT_ALLOWED_NODES
        return []

    @property
    def default_allowed_relationships(self) -> List[str]:
        """获取默认允许的关系类型"""
        if self.is_fault_diagnosis:
            from src.domain.fault_diagnosis_schema import DEFAULT_ALLOWED_RELATIONSHIPS
            return DEFAULT_ALLOWED_RELATIONSHIPS
        return []

    def get_node_labels(self) -> Dict[str, str]:
        """获取所有节点类型及其描述"""
        if self.is_fault_diagnosis:
            from src.domain.fault_diagnosis_schema import AEROSPACE_FAULT_DIAGNOSIS_NODE_LABELS
            return AEROSPACE_FAULT_DIAGNOSIS_NODE_LABELS
        return {}

    def get_relationship_types(self) -> Dict[str, str]:
        """获取所有关系类型及其描述"""
        if self.is_fault_diagnosis:
            from src.domain.fault_diagnosis_schema import AEROSPACE_FAULT_DIAGNOSIS_RELATIONSHIP_TYPES
            return AEROSPACE_FAULT_DIAGNOSIS_RELATIONSHIP_TYPES
        return {}


# ========== 全局配置实例 ==========

_config: DomainConfig = None


def get_domain_config() -> DomainConfig:
    """获取全局领域配置实例"""
    global _config
    if _config is None:
        _config = DomainConfig()
    return _config


def set_domain_config(domain_name: str):
    """设置当前领域配置"""
    global _config
    _config = DomainConfig(domain_name)


def reset_domain_config():
    """重置为默认领域配置"""
    global _config
    _config = DomainConfig()


# ========== 领域特定提示词 ==========


def get_system_prompt_for_graph_extraction(
    use_fault_diagnosis: bool = None,
    allowed_nodes: List[str] = None,
    allowed_relationships: List[str] = None,
) -> str:
    """
    获取知识图谱构建的系统提示词

    Args:
        use_fault_diagnosis: 是否使用故障诊断领域
                               如果为 None，则从配置读取
        allowed_nodes: 允许的节点类型列表
        allowed_relationships: 允许的关系类型列表

    Returns:
        系统提示词
    """
    if use_fault_diagnosis is None:
        use_fault_diagnosis = get_domain_config().is_fault_diagnosis

    if use_fault_diagnosis:
        from src.domain.fault_diagnosis_prompts import (
            FAULT_DIAGNOSIS_SYSTEM_PROMPT,
            FAULT_DIAGNOSIS_EXAMPLES,
        )
        return FAULT_DIAGNOSIS_SYSTEM_PROMPT
    else:
        from src.graph_transformers.llm import GENERAL_SYSTEM_PROMPT
        return GENERAL_SYSTEM_PROMPT


def get_system_prompt_for_schema_extraction(
    use_fault_diagnosis: bool = None,
) -> str:
    """
    获取 Schema 提取的系统提示词

    Args:
        use_fault_diagnosis: 是否使用故障诊断领域
                               如果为 None，则从配置读取

    Returns:
        系统提示词
    """
    if use_fault_diagnosis is None:
        use_fault_diagnosis = get_domain_config().is_fault_diagnosis

    if use_fault_diagnosis:
        from src.domain.fault_diagnosis_prompts import SCHEMA_EXTRACTION_SYSTEM_PROMPT
        return SCHEMA_EXTRACTION_SYSTEM_PROMPT
    else:
        from src.shared.schema_extraction import PROMPT_TEMPLATE_GENERAL
        return PROMPT_TEMPLATE_GENERAL


def get_examples_for_domain(
    use_fault_diagnosis: bool = None,
) -> List[dict]:
    """
    获取领域特定的示例数据

    Args:
        use_fault_diagnosis: 是否使用故障诊断领域
                               如果为 None，则从配置读取

    Returns:
        示例数据列表
    """
    if use_fault_diagnosis is None:
        use_fault_diagnosis = get_domain_config().is_fault_diagnosis

    if use_fault_diagnosis:
        from src.domain.fault_diagnosis_prompts import FAULT_DIAGNOSIS_EXAMPLES
        return FAULT_DIAGNOSIS_EXAMPLES
    else:
        from src.graph_transformers.llm import GENERAL_EXAMPLES
        return GENERAL_EXAMPLES


# ========== 导出函数 ==========


def export_domain_config() -> Dict:
    """导出当前领域配置"""
    config = get_domain_config()
    return {
        "domain_name": config.domain_name,
        "domain_info": config.domain_info,
        "is_fault_diagnosis": config.is_fault_diagnosis,
        "default_allowed_nodes": config.default_allowed_nodes,
        "default_allowed_relationships": config.default_allowed_relationships,
        "available_domains": DOMAINS,
    }


def get_all_available_domains() -> Dict[str, Dict]:
    """获取所有可用的领域"""
    return DOMAINS
