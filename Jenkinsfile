pipeline {
  agent { label 'swiss' }
  stages {
    stage('prepare') {
    steps {
      sh 'docker compose down -v'
      }
    }

    stage('run') {
      steps {
        sh 'docker compose run -d --rm --env-file /var/whisper/.env compose.yml'
      }
    }

    stage('heath-check') {
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
