pipeline {
  agent { label 'swiss' }
    environment {
        IMAGE           = 'dzailz/whisper-api:latest'
        CONTAINER_NAME  = 'whisper-api'
    }

  stages {
    stage('prepare') {
    steps {
      sh '''
        docker_image_id=$(docker images -q "${IMAGE}")

        if [ -n "$docker_image_id" ]; then
            if [ "$(docker stop ${CONTAINER_NAME})" ]; then
                echo "container stopped"
            fi

            if [ "$(docker rmi "$docker_image_id" -f)" ]; then
                echo "image removed"
            fi
        fi
      '''
      }
    }

    stage('run') {
      steps {
        sh 'docker run -d --env-file /var/whisper/.env --name "${CONTAINER_NAME}" --volume ~/models/:/root/.cache/whisper/ -p 8000:8000 --rm "${IMAGE}"'
      }
    }

    stage('test') {
      steps {
        sh '''
        attempt_counter=0
        max_attempts=10

        until { curl --output /dev/null --silent --get --fail http://127.0.0.1:8000; } do
            if [ ${attempt_counter} -eq ${max_attempts} ];then
              echo "Max attempts reached"
              exit 1
            fi

            printf '.'
            attempt_counter=$((attempt_counter + 1))
            sleep 1
        done
        '''
      }
    }
  }
}
