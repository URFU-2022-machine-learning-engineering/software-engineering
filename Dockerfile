FROM python:3.11-slim as requirements-stage
LABEL authors="Vladimir Katin"

ARG POETRY_VERSION="1.7.1"

WORKDIR /tmp

RUN pip install poetry==$POETRY_VERSION && \
    poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-2024-03-04

WORKDIR /app

ENV HOST="0.0.0.0" \
    PORT="8000" \
    PYTHONPATH="/app"

RUN apt update -y \
    && apt install -y --no-install-recommends ffmpeg \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./model ./model
COPY ./api ./api
COPY ./main.py ./main.py

EXPOSE $PORT
# remove --proxy-headers if you don't have a proxy
CMD uvicorn main:app --proxy-headers --host $HOST --port $PORT
