"""
MinIO 客户端模块
用于处理图片上传、下载和管理
"""
import logging
import os
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class MinIOClient:
    """MinIO 客户端封装类"""

    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "llm-graph-images")
        self.use_ssl = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
        self._client = None

    @property
    def client(self):
        """延迟初始化 MinIO 客户端"""
        if self._client is None:
            try:
                self._client = Minio(
                    endpoint=self.endpoint,
                    access_key=self.access_key,
                    secret_key=self.secret_key,
                    secure=self.use_ssl
                )
                logger.info(f"MinIO client initialized: {self.endpoint}")
                # 确保bucket存在
                self._ensure_bucket_exists()
            except S3Error as e:
                logger.error(f"Failed to initialize MinIO client: {e}")
                raise
        return self._client

    def _ensure_bucket_exists(self):
        """确保bucket存在，不存在则创建"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Failed to check/create bucket: {e}")
            raise

    def upload_file(self, file_path: str, object_name: str, content_type: str = None) -> str:
        """
        上传文件到MinIO

        Args:
            file_path: 本地文件路径
            object_name: MinIO中的对象名称
            content_type: 内容类型（可选）

        Returns:
            文件的公开访问URL
        """
        try:
            # 自动检测content_type
            if content_type is None:
                if file_path.endswith('.png'):
                    content_type = 'image/png'
                elif file_path.endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                elif file_path.endswith('.gif'):
                    content_type = 'image/gif'
                elif file_path.endswith('.webp'):
                    content_type = 'image/webp'
                else:
                    content_type = 'application/octet-stream'

            self.client.fput_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                file_path=file_path,
                content_type=content_type
            )

            # 构建URL
            protocol = "https" if self.use_ssl else "http"
            url = f"{protocol}://{self.endpoint}/{self.bucket_name}/{object_name}"
            logger.info(f"Uploaded file: {object_name} -> {url}")
            return url

        except S3Error as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            raise

    def upload_from_bytes(self, data: bytes, object_name: str, content_type: str = None) -> str:
        """
        上传字节流到MinIO

        Args:
            data: 文件字节数据
            object_name: MinIO中的对象名称
            content_type: 内容类型（可选）

        Returns:
            文件的公开访问URL
        """
        try:
            from io import BytesIO

            # 自动检测content_type
            if content_type is None:
                if object_name.endswith('.png'):
                    content_type = 'image/png'
                elif object_name.endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                else:
                    content_type = 'image/png'  # 默认为PNG

            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=BytesIO(data),
                length=len(data),
                content_type=content_type
            )

            # 构建URL
            protocol = "https" if self.use_ssl else "http"
            url = f"{protocol}://{self.endpoint}/{self.bucket_name}/{object_name}"
            logger.info(f"Uploaded bytes: {object_name} -> {url}")
            return url

        except S3Error as e:
            logger.error(f"Failed to upload bytes for {object_name}: {e}")
            raise

    def delete_file(self, object_name: str) -> bool:
        """
        删除MinIO中的文件

        Args:
            object_name: 要删除的对象名称

        Returns:
            是否成功删除
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Deleted file: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Failed to delete file {object_name}: {e}")
            return False

    def get_file_url(self, object_name: str) -> str:
        """
        获取文件的访问URL

        Args:
            object_name: 对象名称

        Returns:
            文件的公开访问URL
        """
        protocol = "https" if self.use_ssl else "http"
        return f"{protocol}://{self.endpoint}/{self.bucket_name}/{object_name}"


# 全局单例实例
_minio_client = None

def get_minio_client() -> MinIOClient:
    """获取MinIO客户端单例"""
    global _minio_client
    if _minio_client is None:
        _minio_client = MinIOClient()
    return _minio_client


# 向后兼容的函数（与现有代码兼容）
def upload_image_to_minio(file_path: str, blob_name: str) -> str:
    """
    上传图片到MinIO（向后兼容的函数）

    Args:
        file_path: 本地文件路径
        blob_name: MinIO中的对象名称

    Returns:
        文件的公开访问URL
    """
    client = get_minio_client()
    return client.upload_file(file_path, blob_name)


def upload_bytes_to_minio(data: bytes, blob_name: str, content_type: str = None) -> str:
    """
    上传字节流到MinIO

    Args:
        data: 文件字节数据
        blob_name: MinIO中的对象名称
        content_type: 内容类型（可选）

    Returns:
        文件的公开访问URL
    """
    client = get_minio_client()
    return client.upload_from_bytes(data, blob_name, content_type)
