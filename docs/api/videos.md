# Users
Supports creating, updating and deleteing videos

## Create a new video
`POST` `/videos/`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
raw_file   | File   | Yes      | Video file to process. Supported formats are: "mp4", "mov", "wmv", "webm", "mkv"

**Response**:

```json
Content-Type application/json
201 Created

{
    "id": 2,
    "file_name": "filename.mp4",
    "raw_file": "http://localhost:8000/media/filename.mp4",
    "uploaded_at": "2021-08-10T11:54:24+0545",
    "outputs": null,
    "thumbnail": "",
    "transcode_status": "Pending"
}
```

## Video List
`GET` `/videos/`

**Response**:

```json
Content-Type application/json
201 Created

{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 2,
            "file_name": "filename.mp4",
            "raw_file": "http://localhost:8000/media/filename.mp4",
            "uploaded_at": "2021-08-10T11:54:24+0545",
            "outputs": null,
            "thumbnail": "",
            "transcode_status": "Pending"
        }
    ]
}

```


## Get users detail
`GET` `/videos/:id`

**Response**:

#### A new video
```json
Content-Type application/json
200 Ok

{
    "id": 2,
    "file_name": "filename.mp4",
    "raw_file": "http://localhost:8000/media/filename.mp4",
    "uploaded_at": "2021-08-10T11:54:24+0545",
    "outputs": null,
    "thumbnail": "",
    "transcode_status": "Pending"
}
```

#### Processing video
```json
Content-Type application/json
200 Ok

{
    "id": 2,
    "file_name": "filename.mp4",
    "raw_file": "http://localhost:8000/media/filename.mp4",
    "uploaded_at": "2021-08-10T11:54:24+0545",
    "outputs": null,
    "thumbnail": "",
    "transcode_status": "Progressing"
}
```

#### Processed video
```json
Content-Type application/json
200 Ok

{
    "id": 2,
    "file_name": "filename.mp4",
    "raw_file": "http://localhost:8000/media/filename.mp4",
    "uploaded_at": "2021-08-10T11:54:24+0545",
    "outputs": [
        {
            "display": "4M",
            "playlist": "https://anurag-video-output.s3.amazonaws.com/converted/filename.mp44M.m3u8",
            "thumbnail": "https://anurag-video-output.s3.amazonaws.com/converted/filename.mp44M-thumb-00001.png"
        },
        {
            "display": "2M",
            "playlist": "https://anurag-video-output.s3.amazonaws.com/converted/filename.mp42M.m3u8",
            "thumbnail": "https://anurag-video-output.s3.amazonaws.com/converted/filename.mp42M-thumb-00001.png"
        },
        {
            "display": "600K",
            "playlist": "https://anurag-video-output.s3.amazonaws.com/converted/filename.mp4600K.m3u8",
            "thumbnail": "https://anurag-video-output.s3.amazonaws.com/converted/filename.mp4600K-thumb-00001.png"
        }
    ],
    "thumbnail": "https://anurag-video-output.s3.amazonaws.com/converted/filename.mp44M-thumb-00001.png",
    "transcode_status": "Complete"
}
```