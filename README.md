# video_uploader-backend
![example workflow](https://github.com/anuragregmi/video-uploader-backend/actions/workflows/test.yml/badge.svg)
[![Built with](https://img.shields.io/badge/Built_with-Cookiecutter_Django_Rest-F7B633.svg)](https://github.com/agconti/cookiecutter-django-rest)

Video Upload an. Check out the project's [documentation](http://anuragregmi.github.io/video-uploader-backend/).

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)  

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
