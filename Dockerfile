FROM python:3.11
LABEL authors="Vladimir Katin"

ENV HOST="0.0.0.0"
ENV PORT="8000"
ENV POETRY_VERSION="1.6.1"

RUN apt update -y  \
    && apt install -y ffmpeg

EXPOSE $PORT
WORKDIR /app

COPY . ./

RUN pip install poetry==$POETRY_VERSION  \
    && poetry install --without="dev"

ENV PYTHONPATH=/app

CMD poetry run uvicorn main:app --host $HOST --port $PORT
