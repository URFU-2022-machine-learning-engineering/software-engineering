IMAGE="dzailz/whisper-api:test-gpu"
ENV_FILE="/var/whisper/.env.local"
CONTAINER_NAME="whisper-api"
MODELS_FOLDER="/var/whisper/whisper_models/models"
OUT_PORT="8000"


function buid_test() {
    docker build -t dzailz/whisper-api:test-gpu -f Dockerfile.gpu .
}

function d_stop() {
  docker stop $CONTAINER_NAME
  docker rm $CONTAINER_NAME
}

function d_pull() {
  docker pull $IMAGE
}

function d_start() {
docker run -d --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 \
--env PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
--env-file $ENV_FILE --name $CONTAINER_NAME --volume $MODELS_FOLDER:/root/.cache/whisper/ \
-p $OUT_PORT:8000 --restart="unless-stopped" $IMAGE

}

if docker ps | grep $CONTAINER_NAME; then
  d_stop
  buid_test
#  d_pull
  d_start
else
  buid_test
#  d_pull
  d_start
fi
