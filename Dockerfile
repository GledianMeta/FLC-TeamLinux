# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.12-alpine AS builder
WORKDIR /app
COPY requirements.txt /app
ENV PORT=8080
ENV HOST="127.0.0.1"
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt \

COPY . /app

ENTRYPOINT ["python3"]
CMD ["start.py"]
