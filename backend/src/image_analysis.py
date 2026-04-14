"""
图片分析模块 - 处理图片查询、base64转换和视觉LLM调用
"""
import base64
import requests
import logging
from typing import List, Dict, Any
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from src.llm import get_llm
from src.shared.constants import CHAT_SYSTEM_TEMPLATE, VISION_LLM_MODEL
from langchain_core.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.graph_query import QUERY_MAP
import os

# 视觉LLM模型配置
VISION_LLM_MODEL = "v-GLM"  # 使用glm-4.6v-flash

# 尝试导入 ZhipuAI 原生客户端
try:
    from zhipuai import ZhipuAI
    ZHIPUAI_AVAILABLE = True
except ImportError:
    ZHIPUAI_AVAILABLE = False
    logging.warning("zhipuai package not installed. Will use ChatOpenAI fallback for vision model.")

def get_image_nodes_with_chunks(graph, document_names: List[str] = None) -> List[Dict[str, Any]]:
    """
    获取所有图片节点及其关联的chunks

    Args:
        graph: Neo4jGraph实例
        document_names: 可选的文档名列表，如果提供则只返回这些文档中的图片

    Returns:
        图片列表，每个图片包含URL和关联的chunks
    """
    try:
        if document_names:
            # 查询特定文档的图片 (c:Chunk) OPTIONAL MATCH (img)-[CONTAINS_IMAGE]-(:Chunk) as c
            query = """
            MATCH (d:Document)-[:PART_OF]->(c:Chunk)-[:CONTAINS_IMAGE]->(img:Image)
            WHERE d.fileName IN $document_names
            OPTIONAL MATCH (img)-[CONTAINS_IMAGE]-(c:Chunk)
            RETURN DISTINCT img.url as img_url,
                   img.fileName as file_name,
                   img.pageNumber as page_number,
                   img.imgIndex as img_index,
                   collect(DISTINCT {
                       chunk_id: c.id,
                       chunk_text: coalesce(c.text, '')
                   }) as chunks
            ORDER BY img.fileName, img.pageNumber, img.imgIndex
            """
            result = graph.query(query, params={"document_names": document_names})
        else:
            # 查询所有图片
            query = """
            MATCH (img:Image)
            OPTIONAL MATCH (img)-[:CONTAINS_IMAGE]-(c:Chunk)
            RETURN DISTINCT img.url as img_url,
                   img.fileName as file_name,
                   img.pageNumber as page_number,
                   img.imgIndex as img_index,
                   collect(DISTINCT {
                       chunk_id: c.id,
                       chunk_text: coalesce(c.text, '')
                   }) as chunks
            ORDER BY img.fileName, img.pageNumber, img.imgIndex
            """
            result = graph.query(query)

        images = []
        for record in result:
            images.append({
                "img_url": record["img_url"],
                "file_name": record["file_name"],
                "page_number": record["page_number"],
                "img_index": record["img_index"],
                "chunks": record["chunks"]
            })

        logging.info(f"Retrieved {len(images)} images")
        return images

    except Exception as e:
        logging.error(f"Error retrieving images: {e}")
        return []


def convert_minio_url_to_base64(minio_url: str) -> str:
    """
    将MinIO本地URL转换为base64编码的data URL

    Args:
        minio_url: MinIO图片URL（如http://localhost:9000/bucket/file.png）

    Returns:
        base64编码的data URL（格式：data:image/png;base64,xxxxx）
    """
    try:
        # 下载图片
        response = requests.get(minio_url, timeout=10)
        response.raise_for_status()

        logging.info(f"Downloading image from {minio_url}")
        logging.info(f"Image size: {len(response.content)} bytes")
        logging.info(f"Content-Type header: {response.headers.get('Content-Type')}")

        # 编码为base64
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        logging.info(f"Base64 length: {len(image_base64)}")

        # 返回data URL格式（与test_api.py保持一致，固定使用image/png）
        # GLM-4.6V 对 Content-Type 有严格要求，简化为 image/png
        data_url = f"data:image/png;base64,{image_base64}"
        logging.info(f"Generated data URL (first 100 chars): {data_url[:100]}...")

        return data_url

    except Exception as e:
        logging.error(f"Error converting MinIO URL to base64: {e}")
        raise Exception(f"Failed to load image from {minio_url}: {str(e)}")


def analyze_image_with_vlm(
    image_url: str,
    user_question: str,
    graph_context: str = ""
) -> Dict[str, Any]:
    """
    使用视觉大模型分析图片

    Args:
        image_url: MinIO图片URL（将自动转换为base64）
        user_question: 用户的问题
        graph_context: 可选的图谱上下文信息

    Returns:
        包含LLM响应和相关QUERY_MAP的字典
    """
    try:
        logging.info(f"Starting image analysis for URL: {image_url}")
        logging.info(f"User question: {user_question}")
        logging.info(f"Graph context length: {len(graph_context)}")

        # 将MinIO URL转换为base64
        if image_url.startswith("http"):
            image_data_url = convert_minio_url_to_base64(image_url)
        else:
            # 已经是data URL格式
            image_data_url = image_url
            logging.info(f"Using provided data URL")

        logging.info(f"Using vision LLM: glm-4.6v")

        # 构建系统提示词
        system_prompt = """You are an AI-powered visual analysis agent specialized in fault diagnosis and technical documentation analysis.

### Task:
1. Analyze the provided image carefully.
2. Identify key elements, components, and any visible technical information.
3. Relate findings to fault diagnosis context if applicable.
4. If graph context is provided, incorporate it into your analysis.

### Response Guidelines:
1. Provide detailed and accurate descriptions of what you see.
2. Identify any fault indicators, warning signs, or anomalies.
3. If relevant, suggest possible causes or related components.
4. When graph context is available, reference specific entities or relationships.
5. For fault diagnosis scenarios, indicate potential failure modes and affected systems.
"""

        # 组合用户问题和上下文
        full_user_question = user_question
        if graph_context:
            full_user_question = f"{user_question}\n\n### Graph Context:\n{graph_context}"

        logging.info(f"Full user question length: {len(full_user_question)}")

        # 使用 ZhipuAI 原生客户端
        if ZHIPUAI_AVAILABLE:
            api_key = os.environ.get('V_ZHIPUAI_API_KEY')
            if not api_key:
                raise Exception("V_ZHIPUAI_API_KEY not found in environment variables")

            client = ZhipuAI(api_key=api_key)
            logging.info(f"ZhipuAI client created successfully")

            # 构建消息 - 与 test_api.py 保持一致，只使用 user 消息
            # 注意：GLM-4.6V 对 system 消息和图片混合可能有兼容性问题
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data_url
                            }
                        },
                        {
                            "type": "text",
                            "text": full_user_question
                        }
                    ]
                }
            ]

            logging.info(f"Calling ZhipuAI API with {len(messages)} messages")
            logging.info(f"Message structure: image_url + text")

            # 调用API - 与 test_api.py 保持一致的参数
            response = client.chat.completions.create(
                model="glm-4.6v",
                messages=messages,
                thinking={
                    "type": "enabled"
                }
            )

            ai_response = response.choices[0].message.content
            logging.info(f"Image analysis completed using ZhipuAI native client")

        else:
            # 回退到使用 ChatOpenAI
            logging.warning("ZhipuAI native client not available, using ChatOpenAI fallback")
            llm, model_name = get_llm(VISION_LLM_MODEL)

            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data_url
                            }
                        },
                        {
                            "type": "text",
                            "text": full_user_question
                        }
                    ]
                }
            ]

            # 调用LLM
            response = llm.invoke(messages)
            ai_response = response.content
            logging.info(f"Image analysis completed using ChatOpenAI fallback")

        # 生成相关的QUERY_MAP建议
        query_map_suggestions = generate_query_map_suggestions(ai_response, graph_context)

        return {
            "response": ai_response,
            "query_map_suggestions": query_map_suggestions,
            "model": "glm-4.6v",
            "mode": "image+graph+vector"
        }

    except Exception as e:
        logging.error(f"Error analyzing image: {e}")
        raise Exception(f"Failed to analyze image: {str(e)}")


def generate_query_map_suggestions(analysis_text: str, graph_context: str) -> Dict[str, str]:
    """
    根据图片分析结果生成QUERY_MAP建议

    Args:
        analysis_text: 视觉LLM的分析结果
        graph_context: 图谱上下文

    Returns:
        QUERY_MAP建议
    """

    # 基于分析内容推断最相关的查询类型
    suggestions = {}

    # 默认建议
    suggestions["docChunkEntities"] = "Full knowledge graph with documents, chunks and entities"
    suggestions["docChunks"] = "Document structure with chunks"
    suggestions["chunks"] = "Connected chunks for detailed content"

    # 如果提到实体，建议实体相关查询
    entity_keywords = ["component", "system", "sensor", "actuator", "fault", "error", "failure"]
    if any(keyword.lower() in analysis_text.lower() for keyword in entity_keywords):
        suggestions["docEntities"] = "Entities extracted from documents"

    # 如果提到关系，建议关系相关查询
    relation_keywords = ["connected", "relationship", "linked", "related", "depends", "part of"]
    if any(keyword.lower() in analysis_text.lower() for keyword in relation_keywords):
        suggestions["chunksEntities"] = "Chunks with their entities"

    return suggestions


def get_image_chunk_context(graph, image_url: str) -> str:
    """
    获取与图片关联的chunks的文本上下文

    Args:
        graph: Neo4jGraph实例
        image_url: 图片URL

    Returns:
        关联chunks的文本内容
    """
    try: #(:Chunk)
        query = """
        MATCH (img:Image {url: $image_url})-[:CONTAINS_IMAGE]-(c:Chunk)
        RETURN collect(DISTINCT c.text) as chunk_texts
        """
        result = graph.query(query, params={"image_url": image_url})

        if result and result[0]["chunk_texts"]:
            return "\n\n".join([text for text in result[0]["chunk_texts"] if text])
        return ""

    except Exception as e:
        logging.error(f"Error getting image chunk context: {e}")
        return ""
