pipeline {
  agent any
  triggers {
    githubPush()
  }
  environment {
    BUILD_NUMBER = "${env.BUILD_NUMBER}" 
  }
  stages {
    stage ('Build & Test') {
      steps {
        script {
          echo "Building the app and testing..."
          sh "docker build -t mayurmohite1/cicd_journal_app:1.0.${BUILD_NUMBER} ."
          // sh '''
          //   docker compose -f compose.yaml up -d
          //   sleep 5
          //   curl -X POST http://localhost:8000/entries \
          //   -H "Content-Type: application/json" \
          //   -d '{
          //       "work": "Kubernetes", 
          //       "struggle": "learning",
          //       "intention": "To build something" 
          //   }'
          //   curl -X GET http://localhost:8000/entries
          //   echo "test successful" 
            
          // '''
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
                echo "test successful"
    '''

        }
      }
    }
    // stage ("Docker push") {
    //   steps {
    //     script {
    //       echo "Pushing to Docker Registry"
    //       def version = "1.0.${BUILD_NUMBER}"
    //       sh "docker push mayurmohite1/cicd_journal_app:${version}"
    //       sh "docker compose -f compose.yaml down"
    //     }
    //   }
    // }
       stage ("Docker push") {
            steps {
              script {
                echo "Pushing to Docker Registry"
                def version = "1.0.${BUILD_NUMBER}"

                withCredentials([usernamePassword(
                  credentialsId: 'dockerhub',
                  usernameVariable: 'DOCKER_USER',
                  passwordVariable: 'DOCKER_PASS'
                )]) {
                  sh '''
                    echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                    docker push mayurmohite1/cicd_journal_app:${version}
                    docker logout
                  '''
                }

                sh "docker compose -f compose.yaml down || true"
              }
            }
          }


      
    stage ("Provisioning") {
      steps {
        script {
          withCredentials([
            string(credentialsId: 'aws_access_key', variable: 'AWS_ACCESS_KEY'),
            string(credentialsId: 'aws_secret_access_key', variable: 'AWS_SECRET_ACCESS_KEY'),
          ]) {
                sh """
                    export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY
                    export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                    cd ./infra && terraform init
                    terraform plan 
                  """
                // sh """
                //     terraform apply -auto-approve \
                //       -var "vpc_cidr_block=${VPC_CIDR}" \
                //       -var "private_subnet_cidr_blocks=${PRIVATE_SUBNETS}" \
                //       -var "public_subnet_cidr_blocks=${PUBLIC_SUBNETS}"
                //     aws eks update-kubeconfig --name (my-cluster) --region (eu-central-1) //get kubeconfig
                //   """

          }
        }
      }
    }
    // stage ('Build Image') {
    //   steps {
    //     echo "building image..."
    //     // script {
    //     //   echo "Building the docker image..."
    //     //   withCredentials([usernamePassword(credentialsId: 'docker_hub', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
    //     //     sh '''
    //     //       docker build -t tanvirj9/test-app:1.0 .
    //     //       echo "$PASS" | docker login -u $USER --password-stdin
    //     //       docker push tanvirj9/test-app:1.0
    //     //     '''
    //     //   } 
    //     // }
    //   }
    // }
    stage ('Deploy') {
      steps {
        script {
          echo "Deploying..."
          // sh """
          //     kubectl apply -f ./k8s/db-configMap.yaml
          //     kubectl apply -f ./k8s/db-init-configMap.yaml
          //     kubectl apply -f ./k8s/db-secret.yaml
          //     kubectl apply -f ./k8s/postgres-deployment.yaml
          //     kubectl apply -f ./k8s/app-deployment.yaml
          //     sleep 10
          //     kubectl get pods
          //     kubectl get svc app-service
          //   """
        }
      }
    }
  }
}
