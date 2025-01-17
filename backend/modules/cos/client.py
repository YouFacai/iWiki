import datetime
import logging
from io import BytesIO

from django.conf import settings
from django.db import IntegrityError
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

from modules.cos.models import UploadLog
from utils.tools import simple_uniq_id

logger = logging.getLogger("cos")


class COSClient(object):
    """对象存储客户端"""

    def __init__(self, operator: str):
        self.operator = operator
        self.client = CosS3Client(
            CosConfig(
                Region=settings.COS_REGION,
                SecretId=settings.TCLOUD_SECRET_ID,
                SecretKey=settings.TCLOUD_SECRET_KEY,
            )
        )
        self.bucket = settings.COS_BUCKET

    def verify_filename(self, filename: str):
        replace_map = {" ": "", "$": "_", "[": "(", "]": ")", "{": "(", "}": ")"}
        for item, new_item in replace_map.items():
            filename = filename.replace(item, new_item)
        if filename.count("(") != filename.count(")") or filename.find(
            ")"
        ) < filename.find("("):
            filename = filename.replace("(", "_").replace(")", "_")
        return filename

    def upload(self, filename: str, file: BytesIO):
        """上传文件"""
        # 文件存储位置
        key = "upload/{date_path}/{random_path}".format(
            date_path=datetime.datetime.now().strftime("%Y%m/%d"),
            random_path=simple_uniq_id(settings.COS_RANDOM_PATH_LENGTH),
        )
        full_path = f"{key}/{filename}"
        # 初始化返回参数
        url = None
        result = False
        try:
            # 创建日志
            log = UploadLog.objects.create(
                name=filename, path=key, operator=self.operator
            )
            # 上传文件
            resp = self.client.put_object(Bucket=self.bucket, Key=full_path, Body=file)
            log.response = resp
            log.save()
            url = "{}/{}".format(settings.COS_DOMAIN, full_path)
            logger.info("Upload File Success %s", url)
            result = True
        except IntegrityError:
            return self.upload(filename, file)
        except Exception as err:
            logger.error("Upload File Error", err)
        return result, url
