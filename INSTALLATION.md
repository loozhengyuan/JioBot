# Quickstart Guide

## Prerequisites
- Docker

## Export environment variables
```sh
export TELEGRAM_BOT_API_TOKEN=secret
export AWS_ACCESS_KEY_ID=secret
export AWS_SECRET_ACCESS_KEY=secret
export INSTANCE_ID=secret
``` 

## Build Docker image
```sh
docker build --tag jiobot:latest .
```

## Create data volume
```sh
docker create volume jiobot-data
```

## Run chatbot
```sh
docker run --mount source=jiobot-data,target=/app/data jiobot
```
_NOTE: For first runs, be sure to add a `--first-run` flag at the end so the pickle files can be created. Terminate the instance (which uploads the first pickle file to AWS S3), remove the `--first-run` flag, and redeploy the instance again. You may also use this same process if you want to 'refresh' your pickle data._