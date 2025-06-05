pipeline {
    agent any

    environment {
        GHCR_TOKEN = credentials('github-personal-access-token')
        GHCR_USER = 'ziyad-mabrouk'
        REPO_NAME = 'openairinterface5g'
        RAN_TAG = 'test'
    }

    stages {
        stage('Build Docker Images') {
            steps {
                script {
                    echo "Building oai-gnb-aw2s:${RAN_TAG} Docker image..."

                    sh """
                        docker build --no-cache --target ran-base --tag ran-base:latest --file docker/Dockerfile.base.ubuntu22 .
                        docker build --no-cache --target ran-build --tag ran-build:latest --file docker/Dockerfile.build.ubuntu22 .
                        docker build --no-cache --target oai-gnb-aw2s --tag oai-gnb-aw2s:${RAN_TAG} --file docker/Dockerfile.gNB.aw2s.ubuntu22 .
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
                        docker tag oai-gnb-aw2s:${RAN_TAG} ghcr.io/\$GHCR_USER/\$REPO_NAME/oai-gnb-aw2s:${RAN_TAG}
                        docker push ghcr.io/\$GHCR_USER/\$REPO_NAME/oai-gnb-aw2s:${RAN_TAG}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Docker image successfully built and pushed to GHCR."
        }
        failure {
            echo "Pipeline failed!"
        }
        always {
            sh 'docker logout'
        }
    }
}
