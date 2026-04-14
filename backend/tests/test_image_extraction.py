"""
图片提取功能测试脚本

用于测试从 PDF 中提取图片并上传到 MinIO 的功能
"""
import os
import sys
import logging
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from document_sources.local_file import get_documents_from_file_by_path
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv
import fitz

# 加载环境变量
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_image_extraction():
    """测试图片提取功能"""
    logger.info("=" * 60)
    logger.info("开始测试图片提取功能")
    logger.info("=" * 60)

    # 测试文件路径（请替换为实际的 PDF 文件）
    test_pdf_path = "test_documents/sample_with_images.pdf"

    if not os.path.exists(test_pdf_path):
        logger.error(f"测试文件不存在: {test_pdf_path}")
        logger.info("请将包含图片的 PDF 文件放在 test_documents 目录下，或修改测试路径")
        return False

    file_name = os.path.basename(test_pdf_path)

    try:
        # 提取文档和图片
        logger.info(f"正在处理文件: {file_name}")
        file_name, pages, file_extension, all_image_info_list = get_documents_from_file_by_path(
            test_pdf_path, file_name
        )

        logger.info(f"文件类型: {file_extension}")
        logger.info(f"提取到 {len(pages)} 页")
        logger.info(f"提取到 {len(all_image_info_list)} 张图片")

        # 打印图片信息
        if all_image_info_list:
            logger.info("\n提取的图片信息:")
            logger.info("-" * 60)
            for img_info in all_image_info_list:
                logger.info(f"  ID: {img_info.get('img_id')}")
                logger.info(f"  URL: {img_info.get('img_url')}")
                logger.info(f"  页码: {img_info.get('page_num')}")
                logger.info(f"  索引: {img_info.get('img_index')}")
                logger.info(f"  尺寸: {img_info.get('width')}x{img_info.get('height')}")
                logger.info(f"  位置: {img_info.get('bbox')}")
                logger.info("-" * 60)
        else:
            logger.warning("未提取到图片")

        # 检查 MinIO 配置
        logger.info("\nMinIO 配置:")
        logger.info(f"  Endpoint: {os.getenv('MINIO_ENDPOINT')}")
        logger.info(f"  Bucket: {os.getenv('MINIO_BUCKET_NAME')}")
        logger.info(f"  Access Key: {os.getenv('MINIO_ACCESS_KEY')}")

        logger.info("\n" + "=" * 60)
        logger.info("测试完成！")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return False


def test_neo4j_image_nodes():
    """测试 Neo4j Image 节点创建"""
    logger.info("=" * 60)
    logger.info("开始测试 Neo4j Image 节点")
    logger.info("=" * 60)

    # Neo4j 连接配置
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7689")
    neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")

    try:
        graph = Neo4jGraph(
            url=neo4j_uri,
            username=neo4j_user,
            password=neo4j_password,
            database=neo4j_database
        )

        # 查询 Image 节点数量
        result = graph.query("MATCH (i:Image) RETURN count(i) as count")
        logger.info(f"当前数据库中有 {result[0]['count']} 个 Image 节点")

        # 查询最近添加的图片
        result = graph.query("""
            MATCH (i:Image)
            RETURN i
            ORDER BY i.id DESC
            LIMIT 5
        """)

        if result:
            logger.info("\n最近的 5 个 Image 节点:")
            for row in result:
                img = row['i']
                logger.info(f"  ID: {img.get('id')}")
                logger.info(f"  URL: {img.get('url')}")
                logger.info(f"  文件: {img.get('fileName')}")
                logger.info(f"  页码: {img.get('pageNumber')}")

        # 查询 Chunk-Image 关系
        result = graph.query("""
            MATCH (c:Chunk)-[r:CONTAINS_IMAGE]->(i:Image)
            RETURN count(r) as count
        """)
        logger.info(f"\n当前有 {result[0]['count']} 个 Chunk-Image 关系")

        logger.info("\n" + "=" * 60)
        logger.info("Neo4j 测试完成！")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.error(f"Neo4j 测试失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "图片提取功能测试" + " " * 34 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # 运行测试
    test_image_extraction()

    print()
    print("按回车键继续 Neo4j 测试，或 Ctrl+C 退出...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n退出测试")
        sys.exit(0)

    test_neo4j_image_nodes()
