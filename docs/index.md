# Video Uploader Backend
![example workflow](https://github.com/anuragregmi/video-uploader-backend/actions/workflows/test.yml/badge.svg)
[![Built with](https://img.shields.io/badge/Built_with-Cookiecutter_Django_Rest-F7B633.svg)](https://github.com/agconti/cookiecutter-django-rest)

Application to Upload videos to s3 and trancode using aws transcoder
# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)
- Configured aws in the system or
    `~/.aws/credentials` should be populated with

```ini
[default]
aws_access_key_id=ACCESSKEYID
aws_secret_access_key=SECRETACCESSKEY
```

# Local Development
Create .env file and write configs
```bash
cp .env.sample .env
```

Start the dev server for local development:
```bash
docker-compose up
```

Run a command inside the docker container:

```bash
docker-compose run --rm web [command]
```
