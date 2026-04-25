import os
import logging
from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)

class MinioUtils:
    _client = None
    
    # 配置从环境变量读取，提供默认值
    ENDPOINT = os.getenv("MINIO_ENDPOINT", "127.0.0.1:9000").replace("http://", "").replace("https://", "")
    ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "rDl9zfGPFvXcYBY5Cmlh")
    SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "294SLh9j7uIJYxoaGCG8asT3W52pq8PXNePZ0ltJ")
    BUCKET = os.getenv("MINIO_BUCKET", "ink-away")
    SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"
    
    # 下载的基础 URL (CDN 或 MinIO 公网地址)
    DOWNLOAD_URL = os.getenv("MINIO_DOWNLOAD_URL", "http://127.0.0.1:9000").rstrip("/")

    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                cls._client = Minio(
                    cls.ENDPOINT,
                    access_key=cls.ACCESS_KEY,
                    secret_key=cls.SECRET_KEY,
                    secure=cls.SECURE
                )
                # 检查桶是否存在，不存在则创建
                if not cls._client.bucket_exists(cls.BUCKET):
                    cls._client.make_bucket(cls.BUCKET)
                    logger.info(f"Created MinIO bucket: {cls.BUCKET}")
            except Exception as e:
                logger.error(f"Failed to initialize MinIO client: {e}")
                return None
        return cls._client

    @classmethod
    def upload_file(cls, local_path, object_name=None):
        """
        上传文件到 MinIO
        :param local_path: 本地文件路径
        :param object_name: 存储的对象名称（如果不传，则取文件名）
        :return: 文件的完整访问 URL，失败返回 None
        """
        client = cls.get_client()
        if not client:
            return None
        
        if not object_name:
            object_name = os.path.basename(local_path)
            
        try:
            # 上传文件
            client.fput_object(
                cls.BUCKET, 
                object_name, 
                local_path,
                content_type=cls._get_content_type(local_path)
            )
            logger.info(f"Successfully uploaded {local_path} to MinIO as {object_name}")
            
            # 拼接下载链接
            # 如果 DOWNLOAD_URL 包含 bucket 名（如某些配置），则直接拼接
            # 否则按照规范拼接：{DOWNLOAD_URL}/{BUCKET}/{OBJECT_NAME}
            if cls.BUCKET in cls.DOWNLOAD_URL:
                 full_url = f"{cls.DOWNLOAD_URL}/{object_name}"
            else:
                 full_url = f"{cls.DOWNLOAD_URL}/{cls.BUCKET}/{object_name}"
            
            return full_url
        except S3Error as e:
            logger.error(f"Error occurred while uploading to MinIO: {e}")
            return None

    @staticmethod
    def _get_content_type(file_path):
        """简单的内容类型识别"""
        ext = os.path.splitext(file_path)[1].lower()
        mapping = {
            ".mp4": "video/mp4",
            ".m4a": "audio/mp4",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png"
        }
        return mapping.get(ext, "application/octet-stream")
