pipeline {
    agent any

    environment {
        GHCR_TOKEN = credentials('github-personal-access-token')
        GHCR_USER = 'ziyad-mabrouk'
        REPO_NAME = 'openairinterface5g'
        RAN_TAG = 'with-metrics'
    }

    stages {
        stage('cleanup') {
            steps {
                sh 'docker system prune -a --volumes --force'
            }
        }
        stage('Build Docker Images') {
            steps {
                script {
                    echo "Building oai-gnb:with-metrics Docker image..."

                    sh """
                        docker build --no-cache --target ran-base --tag ran-base:latest --file docker/Dockerfile.base.ubuntu .
                        docker build --no-cache --target ran-build --tag ran-build:latest --file docker/Dockerfile.build.ubuntu .
                        docker build --no-cache --target oai-gnb --tag oai-gnb:${RAN_TAG} --file docker/Dockerfile.gNB.ubuntu .
                    """
                }
            }
        }

        stage('Login to GHCR') {
            steps {
                script {
                    sh """
                        echo \$GHCR_TOKEN | docker login ghcr.io -u \$GHCR_USER --password-stdin
                    """
                }
            }
        }

        stage('Push Docker Images to GHCR') {
            steps {
                script {
                    echo "Pushing Docker images to GHCR..."

                    sh """
                        docker tag oai-gnb:${RAN_TAG} ghcr.io/\$GHCR_USER/\$REPO_NAME/oai-gnb:${RAN_TAG}
                        docker tag oai-gnb-aw2s:${RAN_TAG} ghcr.io/\$GHCR_USER/\$REPO_NAME/oai-gnb-aw2s:${RAN_TAG}
                        docker tag oai-nr-cuup:${RAN_TAG} ghcr.io/\$GHCR_USER/\$REPO_NAME/oai-nr-cuup:${RAN_TAG}

                        docker push ghcr.io/\$GHCR_USER/\$REPO_NAME/oai-gnb:${RAN_TAG}
                        docker push ghcr.io/\$GHCR_USER/\$REPO_NAME/oai-gnb-aw2s:${RAN_TAG}
                        docker push ghcr.io/\$GHCR_USER/\$REPO_NAME/oai-nr-cuup:${RAN_TAG}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Docker images successfully built and pushed to GHCR."
        }
        failure {
            echo "Pipeline failed!"
        }
        always {
            sh 'docker logout'
        }
    }
}
