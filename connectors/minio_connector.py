import logging

from minio import Minio


class MinioClient:
    def __init__(
        self,
        minio_endpoint: str,
        minio_access_key: str,
        minio_secret_key: str,
        minio_bucket: str,
        minio_use_ssl: bool,
    ):
        self.client = Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=minio_use_ssl,
        )
        self.bucket = minio_bucket

    def get_object(self, object_name: str) -> bytes:
        object_data = None
        object_bytes = b""
        try:
            logging.debug(f"Trying to get an audio file {object_name} from minIO")
            object_data = self.client.get_object(self.bucket, object_name)
            object_bytes = object_data.data
        except Exception as e:
            logging.error(f"Error getting object {object_name}: {e}")
        finally:
            if object_data:
                try:
                    object_data.close()
                    object_data.release_conn()
                except Exception as e:
                    logging.error(f"Error closing object_data: {e}")
                else:
                    logging.info(f"File {object_name} received, connection closed")
        return object_bytes
