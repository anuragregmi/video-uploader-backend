import logging
import boto3

from io import FileIO
from typing import Tuple
from django.conf import settings

from botocore import UNSIGNED
from botocore.client import Config
from botocore.exceptions import ClientError

OUTPUT_KEY_PREFIX = 'converted/'

# PRESET_VAR: Tuple[str]
PRESET_2M: Tuple[str] = ('1351620000001-200010', '2M')
PRESET_1M: Tuple[str] = ('1351620000001-200030', '1M')
PRESET_600K: Tuple[str] = ('1351620000001-200040', '600K')

PRESETS: list = [PRESET_600K, PRESET_1M, PRESET_2M]

def extract_outputs(input_filename: str) -> dict:
    """Generate outputs based on input_filename

    No need to request separately because we know what to expect

    Generates expected files list and verifies them on the bucket
    and adds them on response if exists

    Args:
        input_filename: Input filename passed while calling create_transcode_job

    Return:
        Dict containing outputs and thumbnail
        Sample

            {
                "outputs": [{
                    "playlist": "playlist_url",
                    "thumbnail": "thumbnail_url",
                    "display": "display_name"
                }],
                "thumbnail": "thumbnail_url"
            }

    """
    s3 = boto3.client('s3')
    unsigned_s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))

    def object_exists(key):
        try:
            s3.head_object(Bucket=settings.OUTPUT_BUCKET_NAME, Key=key)
            return True
        except ClientError:
            return False

    def get_url(key):
        # because bucket is public we do not need to sign the url
        return unsigned_s3.generate_presigned_url(
            ClientMethod="get_object",
            ExpiresIn=0,
            Params={
                "Bucket": settings.OUTPUT_BUCKET_NAME,
                "Key": key
            }
        )

    outputs = list()
    for preset_id, preset_name in PRESETS:
        playlist = OUTPUT_KEY_PREFIX + input_filename + preset_name + '.m3u8'
        thumbnail = OUTPUT_KEY_PREFIX + input_filename + preset_name + '-thumb-00001.png'

        if object_exists(playlist):
            playlist_url = get_url(playlist)
            if object_exists(thumbnail):
                thumbnail_url = get_url(thumbnail)
            else:
                thumbnail_url = None
            outputs.append({
                "playlist": playlist_url,
                "thumbnail": thumbnail_url,
                "display": preset_name
            })
        else:
            # this should not occur in normal conditions
            # but may occur when object is deleted manually from the bucket
            # or called before trancoding is complete
            # TODO: log this event
            print(f"Playlist {playlist} not found")
            continue

    if outputs:
        thumbnail = outputs[0]['thumbnail']
    else:
        thumbnail = ''

    print(outputs)
    return {
        "outputs": outputs,
        "thumbnail": thumbnail
    }


def check_job_status(job_id: str) -> str:
    """Check transcode job status

    Args:
        job_id: JobId returned by create_transcode_job

    Returns:
        Job status is one of Submitted , Progressing , Complete , Canceled , or Error
    """
    client = boto3.client('elastictranscoder')
    response: dict = client.read_job(Id=job_id)
    return response['Job']['Status']


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
        OutputKeyPrefix=OUTPUT_KEY_PREFIX,
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
