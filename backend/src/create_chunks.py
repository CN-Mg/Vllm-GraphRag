from langchain_text_splitters import TokenTextSplitter
from langchain.docstore.document import Document
from langchain_community.graphs import Neo4jGraph
import logging
import os
from typing import List, Dict, Any
from src.document_sources.youtube import get_chunks_with_timestamps

logging.basicConfig(format="%(asctime)s - %(message)s", level="INFO")


class CreateChunksofDocument:
    def __init__(self, pages: list[Document], graph: Neo4jGraph):
        self.pages = pages
        self.graph = graph

    def split_file_into_chunks(self) -> List[Document]:
        """
        Split a list of documents(file pages) into chunks of fixed size.

        Returns:
            A list of chunks each of which is a langchain Document.
            图片信息会保留在 chunk 的 metadata 中。
        """
        logging.info("Split file into smaller chunks")

        chunk_size = int(os.environ.get('TEXT_CHUNK_SIZE', 200)) # 默认200 tokens
        chunk_overlap = int(os.environ.get('TEXT_CHUNK_OVERLAP', 20)) # 默认20 tokens
        text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        if 'page' in self.pages[0].metadata:
            chunks = []
            for i, document in enumerate(self.pages):
                page_number = i + 1
                for chunk in text_splitter.split_documents([document]):
                    # 保留原始 document metadata 中的图片信息
                    chunk_metadata = {'page_number': page_number}
                    if 'images' in document.metadata:
                        chunk_metadata['images'] = document.metadata['images']
                    if 'source' in document.metadata:
                        chunk_metadata['source'] = document.metadata['source']
                    if 'filename' in document.metadata:
                        chunk_metadata['filename'] = document.metadata['filename']
                    chunks.append(Document(page_content=chunk.page_content, metadata=chunk_metadata))

        elif 'length' in self.pages[0].metadata:
            chunks_without_timestamps = text_splitter.split_documents(self.pages)
            chunks = get_chunks_with_timestamps(chunks_without_timestamps, self.pages[0].metadata['source'])
        else:
            chunks = text_splitter.split_documents(self.pages)
        return chunks