IMAGE="dzailz/whisper-api:test-gpu"
ENV_FILE="/var/whisper/.env.local"
CONTAINER_NAME="whisper-api"
MODELS_FOLDER="/var/whisper/whisper_models/models"
OUT_PORT="8000"

function d_stop() {
  docker stop $CONTAINER_NAME
  docker rm $CONTAINER_NAME
}

function d_pull() {
  docker pull $IMAGE
}

function d_start() {
  docker run -d \
--gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 \
--env-file $ENV_FILE --name $CONTAINER_NAME --volume $MODELS_FOLDER:/root/.cache/whisper/ \
-p $OUT_PORT:8000 --restart unless-stopped $IMAGE
}

if docker ps | grep $CONTAINER_NAME; then
  d_stop
  d_pull
  d_start
else
  d_pull
  d_start
fi
