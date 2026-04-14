from dataclasses import dataclass
from datetime import datetime

@dataclass
class ImageNode:
    """图片节点实体类，用于存储图片信息"""
    img_id: str = None           # 图片唯一标识符
    img_url: str = None          # MinIO URL
    file_name: str = None        # 源文件名
    page_number: int = None      # 页码
    img_index: int = None        # 当前页面的图片索引
    img_format: str = None       # 图片格式（PNG, JPEG等）
    width: int = None            # 图片宽度（像素）
    height: int = None           # 图片高度（像素）
    bbox: str = None             # 在页面中的边界框坐标 (x0,y0,x1,y1)
    xref: int = None             # PDF中的xref
    created_at: datetime = None  # 创建时间
