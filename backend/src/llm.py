import logging
from langchain.docstore.document import Document
import os
from langchain_openai import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from langchain_groq import ChatGroq
from langchain_google_vertexai import HarmBlockThreshold, HarmCategory
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from langchain_aws import ChatBedrock
from langchain_community.chat_models import ChatOllama
from langchain_community.chat_models.tongyi import ChatTongyi
import google.auth

from src.graph_transformers.llm import LLMGraphTransformer
from src.shared.constants import MODEL_VERSIONS


def get_llm(model_version: str):
    """根据模型名称获取指定的语言模型"""
    env_key = "LLM_MODEL_CONFIG_" + model_version
    env_value = os.environ.get(env_key)
    logging.info("Model: {}".format(env_key))
    model_name = MODEL_VERSIONS[model_version]
    if "Ollama" in model_version:
        # model_name, base_url = env_value.split(",")
        llm = ChatOpenAI(api_key=os.environ.get('OLLAMA_API_KEY'),
                         base_url=os.environ.get('OLLAMA_API_URL'),
                         model=model_name,
                         # top_p=0.7,
                         temperature=0.98)
        
    #elif "GLM" in MODEL_VERSIONS[model_version]:
    elif "glm-4.5-flash" in MODEL_VERSIONS[model_version]:
        llm = ChatOpenAI(api_key=os.environ.get('ZHIPUAI_API_KEY'),
                         base_url=os.environ.get('ZHIPUAI_API_URL'),
                         model=model_name,
                         # top_p=0.7,
                         temperature=0.98)
        
    elif "glm-4.6v" in MODEL_VERSIONS[model_version]:
        llm = ChatOpenAI(api_key=os.environ.get('V_ZHIPUAI_API_KEY'),
                         base_url=os.environ.get('V_ZHIPUAI_API_URL'),
                         model=model_name,
                         # top_p=0.7,
                         temperature=0.98)    

    elif "deepseek" in MODEL_VERSIONS[model_version]:
        llm = ChatOpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),
                         base_url=os.environ.get('DEEPSEEK_API_URL'),
                         model=model_name,
                         top_p=0.7,
                         temperature=0.95)
    elif "qwen" in MODEL_VERSIONS[model_version]:
        llm = ChatOpenAI(api_key=os.environ.get('QWEN_API_KEY'),
                         base_url=os.environ.get('QWEN_API_URL'),
                         model=model_name,
                         top_p=0.7,
                         temperature=0.95
                         )

    elif "gemini" in model_version:
        credentials, project_id = google.auth.default()
        model_name = MODEL_VERSIONS[model_version]
        llm = ChatVertexAI(
            model_name=model_name,
            convert_system_message_to_human=True,
            credentials=credentials,
            project=project_id,
            temperature=0,
            safety_settings={
                HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            },
        )
    elif "openai" in model_version:
        model_name = MODEL_VERSIONS[model_version]
        llm = ChatOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            model=model_name,
            temperature=0,
        )

        llm = ChatBedrock(
            client=bedrock_client, model_id=model_name, model_kwargs=dict(temperature=0)
        )

    logging.info(f"Model created - Model Version: {model_version}")
    return llm, model_name


def get_combined_chunks(chunkId_chunkDoc_list):
    chunks_to_combine = int(os.environ.get("NUMBER_OF_CHUNKS_TO_COMBINE"))
    logging.info(f"Combining {chunks_to_combine} chunks before sending request to LLM")
    combined_chunk_document_list = []
    combined_chunks_page_content = [
        "".join(
            document["chunk_doc"].page_content
            for document in chunkId_chunkDoc_list[i: i + chunks_to_combine]
        )
        for i in range(0, len(chunkId_chunkDoc_list), chunks_to_combine)
    ]
    combined_chunks_ids = [
        [
            document["chunk_id"]
            for document in chunkId_chunkDoc_list[i: i + chunks_to_combine]
        ]
        for i in range(0, len(chunkId_chunkDoc_list), chunks_to_combine)
    ]

    for i in range(len(combined_chunks_page_content)):
        combined_chunk_document_list.append(
            Document(
                page_content=combined_chunks_page_content[i],
                metadata={"combined_chunk_ids": combined_chunks_ids[i]},
            )
        )
    return combined_chunk_document_list


def get_graph_document_list(
        llm, combined_chunk_document_list, allowedNodes, allowedRelationship, use_function=True
):
    futures = []
    graph_document_list = []
    if not use_function:
        node_properties = False
    else:
        node_properties = ["description"]
    llm_transformer = LLMGraphTransformer(
        llm=llm,
        node_properties=node_properties,
        allowed_nodes=allowedNodes,
        allowed_relationships=allowedRelationship,
        use_function_call=use_function
    )
    with ThreadPoolExecutor(max_workers=10) as executor:
        for chunk in combined_chunk_document_list:
            chunk_doc = Document(
                page_content=chunk.page_content.encode("utf-8"), metadata=chunk.metadata
            )
            futures.append(
                executor.submit(llm_transformer.convert_to_graph_documents, [chunk_doc])
            )

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            graph_document = future.result()
            graph_document_list.append(graph_document[0])

    return graph_document_list


def get_graph_from_llm(model, chunkId_chunkDoc_list, allowedNodes, allowedRelationship):
    llm, model_name = get_llm(model)
    combined_chunk_document_list = get_combined_chunks(chunkId_chunkDoc_list)
    graph_document_list = get_graph_document_list(
        llm, combined_chunk_document_list, allowedNodes, allowedRelationship
    )
    return graph_document_list
