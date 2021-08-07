import logging
import boto3

from botocore.exceptions import ClientError
from django.conf import settings
from io import FileIO
from typing import Tuple

PRESET_2M: Tuple[str] = ('1351620000001-200010', '2M')
PRESET_1M: Tuple[str] = ('1351620000001-200030', '1M')
PRESET_600K: Tuple[str] = ('1351620000001-200040', '600K')

PRESETS: list = [PRESET_600K, PRESET_1M, PRESET_2M]

def create_transcode_job(input_filename: str) -> str:
    """Create transcode job in ElasticTranscode

    Args:
        input_filename: file name in Input Bucket (File uploaded after create)

    Return:
        Id of created job
    """
    client = boto3.client('elastictranscoder')
    response: dict = client.create_job(
        PipelineId=settings.PIPELINE_ID,
        Input={
            'Key': input_filename,
            'FrameRate': 'auto',
            'Resolution': 'auto',
            'AspectRatio': 'auto',
            'Interlaced': 'auto',
            'Container': 'auto',
        },
        OutputKeyPrefix='converted/',
        Outputs=[
            {
                'Key': input_filename + preset_name,
                'ThumbnailPattern': input_filename + preset_name + '-thumb-{count}',
                'Rotate': 'auto',
                'PresetId': preset_id,
                'SegmentDuration': '5',
                'Watermarks': [
                    {
                        'PresetWatermarkId': 'BottomRight',
                        'InputKey': settings.WATERMARK_FILE_NAME,
                    },
                ]
            }
            for preset_id, preset_name in PRESETS
        ],
    )
    job_id: str = response["Job"]["Id"]
    return job_id


def upload_file(file: FileIO, bucket: str, object_name=None) -> bool:
    """Upload a file to an S3 bucket

    Args:
        file: File to upload
        bucket: Bucket to upload to
        object_name: S3 object name. If not specified then file_name is used

    Return:
        True if file was uploaded, else False
    """

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_fileobj(file, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
