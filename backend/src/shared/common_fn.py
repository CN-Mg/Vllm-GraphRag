import hashlib
import logging

from modelscope import snapshot_download
from sentence_transformers import SentenceTransformer

from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain_community.graphs import Neo4jGraph
from langchain_community.graphs.graph_document import GraphDocument
from typing import List
import re
import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from langchain_groq import ChatGroq
from langchain_google_vertexai import HarmBlockThreshold, HarmCategory

from minio import Minio
from minio.error import S3Error
# from neo4j.debug import watch
# watch("neo4j")

"""commen_fn.py
- 定义一些通用函数,如Embedding模型加载、URL检查、MinIO上传等"""

# MinIO 配置（建议通过环境变量注入）
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "pdf-images")
MINIO_USE_HTTPS = os.getenv("MINIO_USE_HTTPS", "False") == "True"

def upload_image_to_minio(local_file_path, blob_name):
    """
    上传图片到 MinIO，返回公共访问 URL
    :param local_file_path: 本地临时图片路径
    :param blob_name: MinIO 中的存储路径（如：pdf_images/xxx.png）
    :return: 公开访问 URL
    """
    try:
        # 初始化 MinIO 客户端
        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_USE_HTTPS  # 本地部署设为 False（http），生产可设为 True（https）
        )

        # 检查 Bucket 是否存在，不存在则创建
        if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
            minio_client.make_bucket(MINIO_BUCKET_NAME)
            # 设置 Bucket 公共读（兜底，避免手动配置遗漏）
            minio_client.set_bucket_policy(
                MINIO_BUCKET_NAME,
                '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":["s3:GetObject"],"Resource":["arn:aws:s3:::%s/*"]}]}' % MINIO_BUCKET_NAME
            )

        # 上传文件到 MinIO
        minio_client.fput_object(
            bucket_name=MINIO_BUCKET_NAME,
            object_name=blob_name,
            file_path=local_file_path
        )

        # 生成公共访问 URL（格式：http://<MinIO地址>/<Bucket名>/<文件路径>）
        public_url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}/{blob_name}"
        return public_url

    except S3Error as e:
        raise Exception(f"MinIO 上传失败: {e}")

def check_url_source(source_type, url:str=None):
    """
    Check URL source type and return processed information
    Currently only supports 'web' source type
    """
    try:
      logging.info(f"incoming URL: {url}")

      if source_type == 'web':
        # 基础URL验证
        if not url or not url.startswith(('http://', 'https://')):
            raise Exception('Invalid URL format')
        return url, 'en'  # Default to English

      else:
        raise Exception(f'Unsupported source type: {source_type}')

    except Exception as e:
      logging.error(f"Error in recognize URL: {e}")
      raise Exception(e)


def get_chunk_and_graphDocument(graph_document_list, chunkId_chunkDoc_list):
  logging.info("creating list of chunks and graph documents in get_chunk_and_graphDocument func")
  lst_chunk_chunkId_document=[]
  for graph_document in graph_document_list:            
          for chunk_id in graph_document.source.metadata['combined_chunk_ids'] :
            lst_chunk_chunkId_document.append({'graph_doc':graph_document,'chunk_id':chunk_id})
                  
  return lst_chunk_chunkId_document  
                 
def create_graph_database_connection(uri, userName, password, database):
  enable_user_agent = os.environ.get("ENABLE_USER_AGENT", "False").lower() in ("true", "1", "yes")
  if enable_user_agent:
    graph = Neo4jGraph(url=uri, database=database, username=userName, password=password, refresh_schema=False, sanitize=True,driver_config={'user_agent':os.environ.get('NEO4J_USER_AGENT')})  
  else:
    graph = Neo4jGraph(url=uri, database=database, username=userName, password=password, refresh_schema=False, sanitize=True)    
  return graph

# 从Modelscope中加载embedding模型(Qwen GTE)
def load_embedding_model(embedding_model_name: str):
    if embedding_model_name.startswith("iic"):
        local_dir = "../data/embedding/"
        if not os.path.exists(local_dir):
            model_dir = snapshot_download(embedding_model_name, local_dir=local_dir)
        else:
            model_dir = snapshot_download(embedding_model_name, local_files_only=True, local_dir=local_dir)

        # embeddings = SentenceTransformerEmbeddings(model_name=model_dir, trust_remote_code=True)
        embeddings = SentenceTransformerEmbeddings(model_name=model_dir)
        dimension = 768
        logging.info(f"Embedding: Using modelscope Embeddings{embedding_model_name} , Dimension:{dimension}")
    elif embedding_model_name == "openai":
        embeddings = OpenAIEmbeddings()
        dimension = 1536
        logging.info(f"Embedding: Using OpenAI Embeddings , Dimension:{dimension}")
    elif embedding_model_name == "vertexai":        
        embeddings = VertexAIEmbeddings(
            model="textembedding-gecko@003"
        )
        dimension = 768
        logging.info(f"Embedding: Using Vertex AI Embeddings , Dimension:{dimension}")
    else:
        embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2"#, cache_folder="/embedding_model"
        )
        dimension = 384
        logging.info(f"Embedding: Using SentenceTransformer , Dimension:{dimension}")
    return embeddings, dimension

# 存储节点和关系等_in_neo4j
def save_graphDocuments_in_neo4j(graph:Neo4jGraph, graph_document_list:List[GraphDocument]):
  # graph.add_graph_documents(graph_document_list, baseEntityLabel=True)
  graph.add_graph_documents(graph_document_list)

def delete_uploaded_local_file(merged_file_path, file_name):
  """Delete uploaded local file"""
  file_path = Path(merged_file_path)
  if file_path.exists():
    file_path.unlink()
    logging.info(f'file {file_name} deleted successfully')

def close_db_connection(graph, api_name):
  if not graph._driver._closed:
      logging.info(f"closing connection for {api_name} api")
      # graph._driver.close()

def formatted_time(current_time):
  formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
  return formatted_time