pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        BUILD_NUMBER = "${env.BUILD_NUMBER}" 
        IMAGE_NAME = "mayurmohite1/cicd_journal_app"
        VERSION = "1.0.${BUILD_NUMBER}"
    }

    stages {
        stage('Build & Test') {
            steps {
                script {
                    echo "Building the app and testing..."
                    
                    // Build Docker image with version tag
                    sh "docker build -t ${IMAGE_NAME}:${VERSION} ."
                    // Optionally tag 'latest'
                    sh "docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:latest"

                    // Run tests via docker-compose
                    sh '''
                        docker compose -f compose.yaml down || true
                        docker compose -f compose.yaml up -d
                        sleep 10
                        curl -X POST http://localhost:8000/entries \
                        -H "Content-Type: application/json" \
                        -d '{
                              "work": "Kubernetes",
                              "struggle": "learning",
                              "intention": "To build something"
                          }'
                        curl -X GET http://localhost:8000/entries
                        echo "Test successful"
                    '''
                }
            }
        }

        stage('Docker Push') {
            steps {
                script {
                    echo "Pushing Docker image to registry..."
                    
                    withCredentials([usernamePassword(
                        credentialsId: 'dockerhub', // Make sure this exists in Jenkins
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh """
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker push ${IMAGE_NAME}:${VERSION}
                            docker push ${IMAGE_NAME}:latest
                            docker logout
                        """
                    }

                    // Clean up containers
                    sh "docker compose -f compose.yaml down || true"
                }
            }
        }

        stage('Provisioning') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'aws_access_key', variable: 'AWS_ACCESS_KEY'),
                        string(credentialsId: 'aws_secret_access_key', variable: 'AWS_SECRET_ACCESS_KEY')
                    ]) {
                        sh """
                            export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY
                            export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                            cd ./infra && terraform init
                            terraform plan
                        """
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo "Deploying..."
                    sh '''
                        kubectl apply -f ./k8s/db-configMap.yaml
                        kubectl apply -f ./k8s/db-init-configMap.yaml
                        kubectl apply -f ./k8s/db-secret.yaml
                        kubectl apply -f ./k8s/postgres-deployment.yaml
                        kubectl apply -f ./k8s/app-deployment.yaml
                        sleep 10
                        kubectl get pods
                        kubectl get svc app-service
                    '''

                }
            }
        }
    }

    post {
        success {
            echo "Pipeline finished successfully! Docker image: ${IMAGE_NAME}:${VERSION}"
        }
        failure {
            echo "Pipeline failed!"
        }
    }
}
