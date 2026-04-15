from langchain_community.graphs import Neo4jGraph
from src.make_relationships import create_image_nodes_and_relationships, create_chunk_image_relationships
from src.shared.constants import BUCKET_UPLOAD, PROJECT_ID
from src.shared.schema_extraction import schema_extraction_from_text
from dotenv import load_dotenv
from datetime import datetime
import logging
from src.create_chunks import CreateChunksofDocument
from src.graphDB_dataAccess import graphDBdataAccess
from src.document_sources.local_file import get_documents_from_file_by_path
from src.entities.source_node import sourceNode
from src.generate_graphDocuments_from_llm import generate_graphDocuments
from src.document_sources.web_pages import *
from src.shared.common_fn import *
from src.make_relationships import *
import re
from langchain_community.document_loaders import WebBaseLoader
import warnings
import sys
import shutil
import urllib.parse
import os
from pathlib import Path

warnings.filterwarnings("ignore")
load_dotenv()
logging.basicConfig(format='%(asctime)s - %(message)s',level='INFO')

def upload_file(graph, model, file, chunkNumber, totalChunks, originalname, uri, CHUNK_DIR, MERGED_DIR):
    """
    处理大文件的分块上传

    Args:
        graph: Neo4j图数据库连接
        model: 模型名称
        file: 上传的文件块对象
        chunkNumber: 当前块编号（从1开始）
        totalChunks: 总块数
        originalname: 原始文件名
        uri: 数据库URI
        CHUNK_DIR: 临时存储分块的目录
        MERGED_DIR: 合并后文件的存储目录

    Returns:
        str: 状态消息
    """
    try:
        # 确保目录存在
        os.makedirs(CHUNK_DIR, exist_ok=True)
        os.makedirs(MERGED_DIR, exist_ok=True)

        # 为当前文件创建唯一的子目录（使用原始文件名）
        chunk_subdir = os.path.join(CHUNK_DIR, originalname)
        os.makedirs(chunk_subdir, exist_ok=True)

        # 保存当前块
        chunk_filename = f"chunk_{chunkNumber}_{totalChunks}"
        chunk_path = os.path.join(chunk_subdir, chunk_filename)

        with open(chunk_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            f.flush()

        logging.info(f"Saved chunk {chunkNumber}/{totalChunks} for {originalname}")

        # 检查是否所有块都已接收
        chunk_files = sorted([f for f in os.listdir(chunk_subdir) if f.startswith("chunk_")])
        if len(chunk_files) == int(totalChunks):
            # 所有块已接收，开始合并
            logging.info(f"All chunks received for {originalname}, merging...")

            merged_file_path = os.path.join(MERGED_DIR, originalname)

            with open(merged_file_path, "wb") as merged_file:
                for chunk_file in chunk_files:
                    chunk_path = os.path.join(chunk_subdir, chunk_file)
                    with open(chunk_path, "rb") as chunk:
                        shutil.copyfileobj(chunk, merged_file)

            logging.info(f"File merged successfully: {merged_file_path}")

            # 清理分块目录
            shutil.rmtree(chunk_subdir)

            # 创建源节点
            obj_source_node = sourceNode()
            obj_source_node.file_name = originalname
            obj_source_node.file_source = 'local file'
            obj_source_node.file_type = originalname.split('.')[-1]
            obj_source_node.model = model
            obj_source_node.created_at = datetime.now()

            # 获取文件大小
            file_size = os.path.getsize(merged_file_path)
            obj_source_node.file_size = file_size

            graphDb_data_Access = graphDBdataAccess(graph)
            graphDb_data_Access.create_source_node(obj_source_node)

            return f"All chunks received and merged. Source node created for {originalname}"
        else:
            return f"Chunk {chunkNumber}/{totalChunks} received. Waiting for remaining chunks."

    except Exception as e:
        logging.error(f"Error in upload_file: {e}")
        raise


def create_source_node_graph_web_url(graph, model, source_url, source_type):
    """Create source node for web pages"""
    success_count = 0
    failed_count = 0
    lst_file_name = []

    try:
        pages = WebBaseLoader(source_url, verify_ssl=False).load()
        if pages is None or len(pages) == 0:
            failed_count += 1
            message = f"Unable to read data for given url : {source_url}"
            raise Exception(message)

        obj_source_node = sourceNode()
        obj_source_node.file_type = 'text'
        obj_source_node.file_source = source_type
        obj_source_node.model = model
        obj_source_node.total_pages = 1
        obj_source_node.url = urllib.parse.unquote(source_url)
        obj_source_node.created_at = datetime.now()
        obj_source_node.file_name = pages[0].metadata.get('title', source_url.split('/')[-1])
        obj_source_node.language = pages[0].metadata.get('language', 'en')
        obj_source_node.file_size = sys.getsizeof(pages[0].page_content)

        graphDb_data_Access = graphDBdataAccess(graph)
        graphDb_data_Access.create_source_node(obj_source_node)
        lst_file_name.append({
            'fileName': obj_source_node.file_name,
            'fileSize': obj_source_node.file_size,
            'url': obj_source_node.url,
            'status': 'Success'
        })
        success_count += 1

    except Exception as e:
        logging.error(f"Error processing web URL {source_url}: {e}")
        failed_count += 1
        lst_file_name.append({
            'fileName': source_url.split('/')[-1],
            'fileSize': 0,
            'url': source_url,
            'status': 'Failed'
        })

    return lst_file_name, success_count, failed_count

def extract_graph_from_web_page(graph, model, source_url, allowedNodes, allowedRelationship):
    """Extract graph from web page"""
    try:
        file_name, pages = get_documents_from_web_page(source_url)

        if pages is None or len(pages) == 0:
            raise Exception(f'Content is not available for given URL : {file_name}')

        return processing_source(graph, model, file_name, pages, allowedNodes, allowedRelationship)

    except Exception as e:
        logging.error(f"Error extracting graph from web page {source_url}: {e}")
        raise

def extract_graph_from_file_local_file(graph, model, merged_file_path, fileName, allowedNodes, allowedRelationship, uri):
    """Extract graph from local file"""
    logging.info(f'Process file name: {fileName}')
    all_image_info_list = []

    try:
        file_name, pages, file_extension, all_image_info_list = get_documents_from_file_by_path(merged_file_path, fileName)

        if pages is None or len(pages) == 0:
            raise Exception(f'File content is not available for file: {file_name}')

        return processing_source(graph, model, file_name, pages, allowedNodes, allowedRelationship, True, merged_file_path, uri, all_image_info_list)

    except Exception as e:
        logging.error(f"Error processing local file {fileName}: {e}")
        raise

def processing_source(graph, model, file_name, pages, allowedNodes, allowedRelationship,
                     is_uploaded_from_local=None, merged_file_path=None, uri=None,
                     all_image_info_list=None):
    """
    Process source document and extract knowledge graph
    """
    start_time = datetime.now()
    graphDb_data_Access = graphDBdataAccess(graph)

    # Check current status
    result = graphDb_data_Access.get_current_status_document_node(file_name)

    # Clean text content
    bad_chars = ['"', "\n", "'"]
    for i in range(len(pages)):
        text = pages[i].page_content
        for j in bad_chars:
            if j == '\n':
                text = text.replace(j, ' ')
            else:
                text = text.replace(j, '')
        pages[i] = Document(page_content=str(text), metadata=pages[i].metadata)

    # Split file into chunks
    create_chunks_obj = CreateChunksofDocument(pages, graph)
    chunks = create_chunks_obj.split_file_into_chunks()

    # Create relationships between chunks
    chunkId_chunkDoc_list = create_relation_between_chunks(graph, file_name, chunks)

    # Create image nodes if available
    if all_image_info_list and len(all_image_info_list) > 0:
        create_image_nodes_and_relationships(graph, file_name, all_image_info_list)

        # Create relationships between chunks and images
        chunks_with_images = []
        for chunk_info in chunkId_chunkDoc_list:
            chunk_id = chunk_info['chunk_id']
            chunk_doc = chunk_info['chunk_doc']

            if 'images' in chunk_doc.metadata and chunk_doc.metadata['images']:
                chunks_with_images.append({
                    'chunk_id': chunk_id,
                    'images': chunk_doc.metadata['images']
                })

        if chunks_with_images:
            create_chunk_image_relationships(graph, file_name, chunks_with_images)

    # Process if not already in Processing status
    if result[0]['Status'] != 'Processing':
        # Update source node status
        obj_source_node = sourceNode()
        status = "Processing"
        obj_source_node.file_name = file_name
        obj_source_node.status = status
        obj_source_node.total_chunks = len(chunks)
        obj_source_node.total_pages = len(pages)
        obj_source_node.model = model
        obj_source_node.created_at = datetime.now()

        graphDb_data_Access.update_source_node(obj_source_node)

        # Process chunks in batches
        update_graph_chunk_processed = int(os.environ.get('UPDATE_GRAPH_CHUNKS_PROCESSED', 20))
        is_cancelled_status = False
        job_status = "Completed"
        node_count = 0
        rel_count = 0

        for i in range(0, len(chunkId_chunkDoc_list), update_graph_chunk_processed):
            select_chunks_upto = min(i + update_graph_chunk_processed, len(chunkId_chunkDoc_list))
            logging.info(f'Selected Chunks up to: {select_chunks_upto}')

            result = graphDb_data_Access.get_current_status_document_node(file_name)
            is_cancelled_status = result[0]['is_cancelled']

            if bool(is_cancelled_status):
                job_status = "Cancelled"
                logging.info('Job cancelled by user')
                break
            else:
                node_count, rel_count = processing_chunks(
                    chunkId_chunkDoc_list[i:select_chunks_upto],
                    graph, file_name, model, allowedNodes, allowedRelationship,
                    node_count, rel_count
                )

                # Update progress
                end_time = datetime.now()
                processed_time = end_time - start_time

                obj_source_node = sourceNode()
                obj_source_node.file_name = file_name
                obj_source_node.updated_at = end_time
                obj_source_node.processing_time = processed_time
                obj_source_node.node_count = node_count
                obj_source_node.processed_chunk = select_chunks_upto
                obj_source_node.relationship_count = rel_count
                graphDb_data_Access.update_source_node(obj_source_node)

        # Final status update
        result = graphDb_data_Access.get_current_status_document_node(file_name)
        is_cancelled_status = result[0]['is_cancelled']
        if bool(is_cancelled_status):
            job_status = 'Cancelled'
            logging.info('Job cancelled at the end of extraction')
        else:
            logging.info(f'Job Status at the end: {job_status}')

        end_time = datetime.now()
        processed_time = end_time - start_time

        # Final update
        obj_source_node = sourceNode()
        obj_source_node.file_name = file_name
        obj_source_node.status = job_status
        obj_source_node.processing_time = processed_time
        graphDb_data_Access.update_source_node(obj_source_node)

        logging.info('Updated the nodeCount and relCount properties in Document node')
        logging.info(f'File: {file_name} extraction has been completed')

        # Clean up local files if uploaded from local
        if is_uploaded_from_local:
            delete_uploaded_local_file(merged_file_path, file_name)

        return {
            "fileName": file_name,
            "nodeCount": node_count,
            "relationshipCount": rel_count,
            "processingTime": round(processed_time.total_seconds(), 2),
            "status": job_status,
            "model": model,
            "success_count": 1
        }
    else:
        logging.info('File does not process because it\'s already in Processing status')
        return None

def processing_chunks(chunkId_chunkDoc_list, graph, file_name, model, allowedNodes, allowedRelationship,
                      node_count, rel_count):
    """Process chunks and generate graph documents"""
    # Update embedding and create vector index
    update_embedding_create_vector_index(graph, chunkId_chunkDoc_list, file_name)

    logging.info("Get graph document list from models")
    graph_documents = generate_graphDocuments(model, graph, chunkId_chunkDoc_list, allowedNodes, allowedRelationship)

    # Save graph documents
    save_graphDocuments_in_neo4j(graph, graph_documents)

    # Create relationships between chunks and entities
    chunks_and_graphDocuments_list = get_chunk_and_graphDocument(graph_documents, chunkId_chunkDoc_list)
    merge_relationship_between_chunk_and_entites(graph, chunks_and_graphDocuments_list)

    # Count nodes and relationships
    distinct_nodes = set()
    relations = []
    for graph_document in graph_documents:
        # Get distinct nodes
        for node in graph_document.nodes:
            node_id = node.id
            node_type = node.type
            if (node_id, node_type) not in distinct_nodes:
                distinct_nodes.add((node_id, node_type))

        # Get all relations
        for relation in graph_document.relationships:
            relations.append(relation.type)

    node_count += len(distinct_nodes)
    rel_count += len(relations)

    logging.info(f'Node count: {node_count}, Relation count: {rel_count}')
    return node_count, rel_count

def get_source_list_from_graph(uri, userName, password, db_name=None):
    """Get list of sources from the graph"""
    logging.info("Get existing files list from graph")
    graph = Neo4jGraph(url=uri, database=db_name, username=userName, password=password)
    graph_DB_dataAccess = graphDBdataAccess(graph)

    if not graph._driver._closed:
        logging.info("Closing connection for sources_list api")

    return graph_DB_dataAccess.get_source_list()

def update_graph(graph):
    """Update graph with KNN relationships"""
    graph_DB_dataAccess = graphDBdataAccess(graph)
    graph_DB_dataAccess.update_KNN_graph()

def connection_check(graph):
    """Check connection to Neo4j"""
    graph_DB_dataAccess = graphDBdataAccess(graph)
    return graph_DB_dataAccess.connection_check()

def get_labels_and_relationtypes(graph):
    """Get all labels and relationship types from the graph"""
    query = """
    RETURN collect {
    CALL db.labels() yield label
    WHERE NOT label IN ['Chunk','_Bloom_Perspective_']
    return label order by label limit 100 } as labels,
    collect {
    CALL db.relationshipTypes() yield relationshipType as type
    WHERE NOT type IN ['PART_OF', 'NEXT_CHUNK', 'HAS_ENTITY', '_Bloom_Perspective_']
    return type order by type LIMIT 100 } as relationshipTypes
    """
    graphDb_data_Access = graphDBdataAccess(graph)
    result = graphDb_data_Access.execute_query(query)
    if result is None:
        result = []
    return result

def manually_cancelled_job(graph, filenames, source_types, merged_dir, uri):
    """Manually cancel processing jobs"""
    filename_list = list(map(str.strip, json.loads(filenames)))
    source_types_list = list(map(str.strip, json.loads(source_types)))
    gcs_file_cache = os.environ.get('GCS_FILE_CACHE')

    for (file_name, source_type) in zip(filename_list, source_types_list):
        obj_source_node = sourceNode()
        obj_source_node.file_name = file_name
        obj_source_node.is_cancelled = True
        obj_source_node.status = 'Cancelled'
        obj_source_node.updated_at = datetime.now()

        graphDb_data_Access = graphDBdataAccess(graph)
        graphDb_data_Access.update_source_node(obj_source_node)

        # Clean up files
        if source_type == 'local file':
            if gcs_file_cache == 'True':
                logging.warning("GCS integration removed. Using local file deletion instead.")
                folder_name = create_gcs_bucket_folder_name_hashed(uri, file_name)
                logging.info(f'Skipped GCS cleanup for {file_name}')
            else:
                merged_file_path = os.path.join(merged_dir, file_name)
                if os.path.exists(merged_file_path):
                    os.remove(merged_file_path)
                    logging.info(f'Deleted file: {merged_file_path}')

    return "Cancelled the processing job successfully"

def populate_graph_schema_from_text(text, model, is_schema_description_cheked):
    """Extract schema from text"""
    result = schema_extraction_from_text(text, model, is_schema_description_cheked)
    return {"labels": result.labels, "relationshipTypes": result.relationshipTypes}