"""
领域特定模块 - 航空航天与机械故障诊断
"""

# Schema 和 Prompts
from .fault_diagnosis_schema import (
    AEROSPACE_FAULT_DIAGNOSIS_NODE_LABELS,
    AEROSPACE_FAULT_DIAGNOSIS_RELATIONSHIP_TYPES,
    DEFAULT_ALLOWED_NODES,
    DEFAULT_ALLOWED_RELATIONSHIPS,
    get_node_description,
    get_relationship_description,
    get_schema_for_export,
)

from .fault_diagnosis_prompts import (
    SCHEMA_EXTRACTION_SYSTEM_PROMPT,
    GRAPH_EXTRACTION_SYSTEM_PROMPT,
    FAULT_DIAGNOSIS_EXAMPLES,
    get_schema_extraction_prompt,
    get_graph_extraction_prompt,
    get_fault_diagnosis_examples,
    get_node_examples_by_type,
    get_relationship_examples_by_type,
)

# 配置
from .config import (
    DomainConfig,
    get_domain_config,
    set_domain_config,
    reset_domain_config,
    get_system_prompt_for_graph_extraction,
    get_system_prompt_for_schema_extraction,
    get_examples_for_domain,
    export_domain_config,
    get_all_available_domains,
    DOMAINS,
)

__all__ = [
    # Schema
    "AEROSPACE_FAULT_DIAGNOSIS_NODE_LABELS",
    "AEROSPACE_FAULT_DIAGNOSIS_RELATIONSHIP_TYPES",
    "DEFAULT_ALLOWED_NODES",
    "DEFAULT_ALLOWED_RELATIONSHIPS",
    "get_node_description",
    "get_relationship_description",
    "get_schema_for_export",
    # Prompts
    "SCHEMA_EXTRACTION_SYSTEM_PROMPT",
    "GRAPH_EXTRACTION_SYSTEM_PROMPT",
    "FAULT_DIAGNOSIS_EXAMPLES",
    "get_schema_extraction_prompt",
    "get_graph_extraction_prompt",
    "get_fault_diagnosis_examples",
    "get_node_examples_by_type",
    "get_relationship_examples_by_type",
    # Configuration
    "DomainConfig",
    "get_domain_config",
    "set_domain_config",
    "reset_domain_config",
    "get_system_prompt_for_graph_extraction",
    "get_system_prompt_for_schema_extraction",
    "get_examples_for_domain",
    "export_domain_config",
    "get_all_available_domains",
    "DOMAINS",
]
