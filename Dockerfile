FROM python:3.11
LABEL authors="Vladimir Katin"

ARG POETRY_VERSION="1.7.1"

ENV HOST="0.0.0.0" \
    PORT="8000" \
    PYTHONPATH="/app" \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="$POETRY_HOME/bin:$PATH"

RUN apt update -y \
    && apt install -y --no-install-recommends ffmpeg \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY . ./

RUN pip install poetry==$POETRY_VERSION  \
    && poetry install --without="dev"

EXPOSE $PORT

CMD poetry run uvicorn main:app --host $HOST --port $PORT

