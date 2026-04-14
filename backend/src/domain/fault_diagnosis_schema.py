"""
航空航天与机械故障诊断与健康管理领域 Schema 定义

包含节点类型、关系类型和提取规则
"""

# ========== 节点类型 (Node Labels) ==========

AEROSPACE_FAULT_DIAGNOSIS_NODE_LABELS = {
    # 设备与组件类
    "Equipment": "主要设备或系统，如发动机、起落架、液压系统等",
    "Component": "组成设备的子组件，如泵、阀门、传感器等",
    "Subsystem": "系统的子系统，如燃油系统、润滑系统等",
    "Part": "更小的零件或部件",

    # 故障与问题类
    "Fault": "具体的故障现象或事件",
    "FailureMode": "故障模式，描述故障发生的机理或类型",
    "Symptom": "故障症状或表现",
    "Error": "错误码或错误信息",
    "Anomaly": "异常状态或偏离正常的情况",
    "Defect": "缺陷或质量问题",

    # 诊断与维修类
    "Diagnosis": "诊断结果或诊断过程",
    "Solution": "解决方案或修复措施",
    "Maintenance": "维护活动或程序",
    "Repair": "维修操作",
    "Procedure": "具体的操作程序或步骤",
    "Troubleshooting": "故障排除流程",

    # 状态与监测类
    "Parameter": "可监测的参数，如温度、压力、振动等",
    "Sensor": "传感器或监测设备",
    "Threshold": "阈值或限值",
    "Measurement": "测量值或读数",
    "Indicator": "性能指标或健康指标",
    "Trend": "趋势或变化模式",
    "Alarm": "报警或警告",

    # 原因与条件类
    "Cause": "故障原因",
    "Condition": "工作条件或环境条件",
    "Trigger": "触发因素或事件",
    "Risk": "风险评估",
    "SafetyIssue": "安全问题",

    # 文档与信息类
    "Document": "文档",
    "Manual": "技术手册",
    "Regulation": "法规或规范",
    "Standard": "技术标准",
    "Specification": "技术规格",
    "Instruction": "操作说明",

    # 位置与时间类
    "Location": "位置或区域",
    "Phase": "飞行阶段或运行阶段",
    "TimeWindow": "时间窗口",

    # 其他
    "Tool": "工具或设备",
    "Material": "材料或消耗品",
    "Reference": "参考信息或交叉引用",
}

# ========== 关系类型 (Relationship Types) ==========

AEROSPACE_FAULT_DIAGNOSIS_RELATIONSHIP_TYPES = {
    # 包含与组成关系
    "CONTAINS": "包含（设备包含组件）",
    "COMPOSED_OF": "由...组成",
    "PART_OF": "是...的一部分",
    "CONNECTED_TO": "连接到",

    # 故障与症状关系
    "HAS_FAULT": "有故障",
    "CAUSES": "导致（故障导致后果）",
    "RESULT_FROM": "由...导致",
    "MANIFESTS_AS": "表现为（故障表现为症状）",
    "INDICATES": "指示（参数指示故障）",
    "PRECEDES": "先于（故障模式先于其他故障）",
    "ACCOMPANIED_BY": "伴随（故障伴随其他问题）",

    # 诊断与解决关系
    "DIAGNOSES_AS": "诊断为",
    "SUGGESTS": "建议（诊断建议解决方案）",
    "REQUIRES": "需要（维修需要工具/材料）",
    "USES": "使用（程序使用工具）",
    "RESOLVES": "解决（方案解决故障）",
    "PREVENTS": "预防（维护预防故障）",
    "VALIDATES": "验证（验证诊断结果）",

    # 监测与测量关系
    "MONITORS": "监测（传感器监测参数）",
    "MEASURES": "测量（测量设备测量参数）",
    "EXCEEDS": "超过（测量超过阈值）",
    "APPROACHES": "接近（测量接近阈值）",
    "CORRELATES_WITH": "相关于（参数之间相关）",
    "TRENDS": "趋势（参数呈现趋势）",
    "TRIGGERS": "触发（条件触发报警）",

    # 位置与时间关系
    "LOCATED_IN": "位于",
    "OCCURS_DURING": "发生在...阶段",
    "AFFECTS": "影响（故障影响设备）",
    "ASSOCIATED_WITH": "关联于",

    # 原因与条件关系
    "CAUSED_BY": "由...引起",
    "RELATED_TO_CAUSE": "与...原因相关",
    "CONDITIONS_FOR": "是...的条件",
    "INCREASES_RISK": "增加风险",

    # 文档与引用关系
    "DESCRIBED_IN": "在...中描述",
    "REFERENCED_IN": "在...中引用",
    "COMPLIES_WITH": "符合...标准",
    "EXEMPTS_FROM": "豁免于...规定",

    # 其他关系
    "HAS_SPECIFICATION": "有规格说明",
    "REQUIRES_INSPECTION": "需要检查",
    "REPLACES": "替换",
    "UPGRADES": "升级",
}

# ========== 节点属性定义 ==========

# 常用属性模板
NODE_PROPERTY_TEMPLATES = {
    "Equipment": {
        "model": "型号",
        "serial_number": "序列号",
        "manufacturer": "制造商",
        "category": "类别",
        "status": "状态",
        "service_hours": "运行小时数",
        "installation_date": "安装日期",
        "last_maintenance": "上次维护日期",
    },
    "Fault": {
        "severity": "严重程度（Critical/High/Medium/Low）",
        "status": "状态（Active/Resolved/Investigating）",
        "occurrence_date": "发生日期",
        "frequency": "发生频率",
        "impact": "影响描述",
    },
    "Parameter": {
        "unit": "单位",
        "normal_range": "正常范围",
        "critical_range": "临界范围",
        "data_type": "数据类型（Analog/Digital）",
        "sample_rate": "采样率",
    },
    "Sensor": {
        "type": "传感器类型",
        "location": "安装位置",
        "accuracy": "精度",
        "range": "测量范围",
    },
}

# ========== Schema 生成配置 ==========

# 默认允许的节点类型（可根据需要过滤）
DEFAULT_ALLOWED_NODES = list(AEROSPACE_FAULT_DIAGNOSIS_NODE_LABELS.keys())

# 默认允许的关系类型（可根据需要过滤）
DEFAULT_ALLOWED_RELATIONSHIPS = list(AEROSPACE_FAULT_DIAGNOSIS_RELATIONSHIP_TYPES.keys())

# 常用节点组合（用于前端展示或快速过滤）
COMMON_NODE_COMBINATIONS = {
    "fault_analysis": ["Fault", "FailureMode", "Symptom", "Cause", "Diagnosis", "Solution"],
    "monitoring": ["Sensor", "Parameter", "Measurement", "Threshold", "Alarm"],
    "maintenance": ["Equipment", "Component", "Maintenance", "Repair", "Procedure", "Tool"],
    "documentation": ["Document", "Manual", "Regulation", "Standard", "Instruction"],
}


def get_node_description(label: str) -> str:
    """获取节点类型的中文描述"""
    return AEROSPACE_FAULT_DIAGNOSIS_NODE_LABELS.get(label, label)


def get_relationship_description(relation: str) -> str:
    """获取关系类型的中文描述"""
    return AEROSPACE_FAULT_DIAGNOSIS_RELATIONSHIP_TYPES.get(relation, relation)


def get_schema_for_export() -> dict:
    """导出完整的 Schema 定义"""
    return {
        "nodes": AEROSPACE_FAULT_DIAGNOSIS_NODE_LABELS,
        "relationships": AEROSPACE_FAULT_DIAGNOSIS_RELATIONSHIP_TYPES,
        "property_templates": NODE_PROPERTY_TEMPLATES,
        "defaults": {
            "allowed_nodes": DEFAULT_ALLOWED_NODES,
            "allowed_relationships": DEFAULT_ALLOWED_RELATIONSHIPS,
        },
    }
