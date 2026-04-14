import logging
import shutil
import os
import fitz  # PyMuPDF
import uuid
import tempfile
from typing import Dict, List, Any, Tuple

from pathlib import Path
from tempfile import NamedTemporaryFile
# from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_core.documents import Document
from src.shared.common_fn import upload_image_to_minio  # 替换原 GCS/OSS 导入

def extract_images_from_pdf_page(page, page_num: int, file_name: str) -> List[Dict[str, Any]]:
    """
    提取 PDF 图片并上传到 MinIO

    Args:
        page: PyMuPDF 页面对象
        page_num: 页码（从1开始）
        file_name: 文件名

    Returns:
        图片信息列表，每个包含 img_id, img_url, page_num, img_index, bbox等
    """
    image_info_list = []

    try:
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]

            # 获取图片在页面中的位置信息
            image_rects = page.get_image_rects(xref)
            bbox = None
            if image_rects:
                rect = image_rects[0]  # 使用第一个位置
                bbox = f"{round(rect.x0, 2)},{round(rect.y0, 2)},{round(rect.x1, 2)},{round(rect.y1, 2)}"

            # 获取图片对象
            base_image = fitz.Pixmap(page.parent, xref)

            # 跳过CMYK图片（不支持保存为PNG）
            if base_image.n >= 5:
                base_image = fitz.Pixmap(fitz.csRGB, base_image)

            # 生成唯一图片 ID
            img_id = f"{file_name}_page{page_num}_img{img_index}_{uuid.uuid4().hex[:8]}"

            # 临时保存图片（使用跨平台临时目录）
            tmp_dir = tempfile.gettempdir()
            tmp_img_path = os.path.join(tmp_dir, f"{img_id}.png")
            base_image.save(tmp_img_path)

            # 获取图片尺寸
            width = base_image.width
            height = base_image.height

            # 上传到 MinIO
            # 注意：bucket 名称已经是 pdf-images，所以 blob_name 不需要再包含 pdf_images 前缀
            blob_name = f"{file_name}/{img_id}.png"
            img_url = upload_image_to_minio(tmp_img_path, blob_name)

            # 收集图片信息
            image_info = {
                "img_id": img_id,
                "img_url": img_url,
                "page_num": page_num,
                "img_index": img_index,
                "file_name": file_name,
                "img_format": "png",
                "width": width,
                "height": height,
                "bbox": bbox,
                "xref": xref
            }
            image_info_list.append(image_info)

            # 清理临时文件
            os.remove(tmp_img_path)

            # 释放内存
            base_image = None

    except Exception as e:
        logging.warning(f"Error extracting images from page {page_num}: {e}")

    return image_info_list

def load_document_content(file_path):
    if Path(file_path).suffix.lower() == '.pdf':
        print("in if")
        return PyMuPDFLoader(file_path)
    else:
        print("in else")
        return UnstructuredFileLoader(file_path, encoding="utf-8", mode="elements")
    
def get_documents_from_file_by_path(file_path, file_name) -> Tuple[str, List[Document], str, List[Dict[str, Any]]]:
    """
    从文件路径获取文档内容，同时提取图片信息

    Args:
        file_path: 文件路径
        file_name: 文件名

    Returns:
        Tuple: (file_name, pages, file_extension, all_image_info_list)
        - file_name: 文件名
        - pages: Document 对象列表
        - file_extension: 文件扩展名
        - all_image_info_list: 所有提取的图片信息列表
    """
    file_path = Path(file_path)
    all_image_info_list = []

    if file_path.exists():
        logging.info(f'file {file_name} processing')
        file_extension = file_path.suffix.lower()

        try:
            if file_extension == ".pdf":
                # PDF文件：使用 PyMuPDF 提取文字和图片
                doc = fitz.open(file_path)
                pages = []

                for page_num in range(len(doc)):
                    page = doc[page_num]

                    # 提取文字内容
                    text = page.get_text("text")

                    # 提取图片并生成URL
                    img_info_list = extract_images_from_pdf_page(page, page_num + 1, file_name)
                    all_image_info_list.extend(img_info_list)

                    # 构造Document对象，metadata中加入图片信息
                    metadata = {
                        "source": str(file_path),
                        "page_number": page_num + 1,
                        "filename": file_name,
                        "filetype": "pdf",
                        "total_pages": len(doc),
                        "images": img_info_list  # 当前页的图片列表
                    }

                    pages.append(Document(page_content=text, metadata=metadata))

                doc.close()

                logging.info(f"Extracted {len(all_image_info_list)} images from {file_name}")

            else:
                # 非PDF文件：原有逻辑
                loader = UnstructuredFileLoader(file_path, encoding="utf-8", mode="elements")
                unstructured_pages = loader.load()
                pages = get_pages_with_page_numbers(unstructured_pages)

                # 非PDF文件暂不支持图片提取
                all_image_info_list = []

        except Exception as e:
            raise Exception(f'Error while reading the file content or metadata: {str(e)}')
    else:
        logging.info(f'File {file_name} does not exist')
        raise Exception(f'File {file_name} does not exist')

    return file_name, pages, file_extension, all_image_info_list


def get_document_with_images(file_path, file_name) -> Tuple[str, List[Document], str, List[Dict[str, Any]]]:
    """
    公开接口：获取文档内容和图片信息（与 get_documents_from_file_by_path 相同）

    Args:
        file_path: 文件路径
        file_name: 文件名

    Returns:
        (file_name, pages, file_extension, all_image_info_list)
    """
    return get_documents_from_file_by_path(file_path, file_name)

def get_pages_with_page_numbers(unstructured_pages):
    pages = []
    page_number = 1
    page_content=''
    metadata = {}
    for page in unstructured_pages:
        if  'page_number' in page.metadata:
            if page.metadata['page_number']==page_number:
                page_content += page.page_content
                metadata = {'source':page.metadata['source'],'page_number':page_number, 'filename':page.metadata['filename'],
                        'filetype':page.metadata['filetype'], 'total_pages':unstructured_pages[-1].metadata['page_number']}
                
            if page.metadata['page_number']>page_number:
                page_number+=1
                if not metadata:
                    metadata = {'total_pages':unstructured_pages[-1].metadata['page_number']}
                pages.append(Document(page_content = page_content, metadata=metadata))
                page_content='' 
                
            if page == unstructured_pages[-1]:
                if not metadata:
                    metadata = {'total_pages':unstructured_pages[-1].metadata['page_number']}
                pages.append(Document(page_content = page_content, metadata=metadata))
                    
        elif page.metadata['category']=='PageBreak' and page!=unstructured_pages[0]:
            page_number+=1
            pages.append(Document(page_content = page_content, metadata=metadata))
            page_content=''
            metadata={}
        
        else:
            page_content += page.page_content
            metadata_with_custom_page_number = {'source':page.metadata['source'],
                            'page_number':1, 'filename':page.metadata['filename'],
                            'filetype':page.metadata['filetype'], 'total_pages':1}
            if page == unstructured_pages[-1]:
                    pages.append(Document(page_content = page_content, metadata=metadata_with_custom_page_number))
    return pages                

# def get_documents_from_file_by_bytes(file):
#     file_name = file.filename
#     logging.info(f"get_documents_from_file called for filename = {file_name}")
#     suffix = Path(file.filename).suffix
#     with NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
#         shutil.copyfileobj(file.file, tmp)
#         tmp_path = Path(tmp.name)
#         loader = PyPDFLoader(str(tmp_path))
#         pages = loader.load_and_split()
#     return file_name, pages
