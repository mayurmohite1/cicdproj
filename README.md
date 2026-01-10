# Capstone Project:
This capstone project demonstrates the complete end-to-end workflow of building, containerizing, and deploying a full-stack journal application using modern DevOps and cloud-native tools. The project covers the entire lifecycle—from Dockerization and local testing to Kubernetes manifest creation, infrastructure provisioning with Terraform, and an automated CI/CD workflow using Jenkins. The application is deployed on an Amazon EKS cluster, with Jenkins handling continuous integration, automated image versioning, and continuous deployment. This setup reflects real-world cloud DevOps practices and emphasizes scalability, automation, and infrastructure-as-code principles.<br/>

The system is designed to evolve, with future enhancements planned for secret management using HashiCorp Vault, monitoring with Prometheus and Grafana, and improved security controls.

# Prerequisites
The following knowledge, tools and accounts are required for this project: <br/>

## Technical Knowledge
- Basic understanding of Docker and Docker Compose
- Familiarity with Kubernetes concepts (Deployments, Services, ConfigMaps, Secrets)
- Understanding of Terraform fundamentals
- Basic AWS knowledge (IAM, VPC, EKS, EC2)
- Understanding of CI/CD pipelines and Jenkins

## Required Tools Installed
- Docker & Docker Compose
- Terraform
- kubectl
- AWS CLI
- Git & GitHub
- ngrok (for local webhook exposure)

## Accounts & Services
- Docker Hub account (for storing images)
- AWS account with programmatic access
- GitHub repository for the application and pipeline

If the pre-requisites are met, then the project can be done without any issues.

## 1. Containerizing the application and pushing to dockerhub
The first thing that starts this project is to create a Dockerfile that is used to build the image 'tanvirj9/journal-app:1.0'. <br>
`docker build -t tanvirj9/journal-app:1.0 .` <br>

The app is tested locally using the `compose.yaml` file. <br>
`docker-compose -f compose.yaml up` <br>
Following curl command are used to test if the app and postgres is working properly.
1. Create a post:  
   ```bash
   curl -X POST http://host.docker.internal:8000/entries \
   -H "Content-Type: application/json" \
   -d '{
      "work": "Kubernetes", 
      "struggle": "learning",
      "intention": "To build something" 
   }'

2. Get the post:
   ```bash
   curl -X GET http://host.docker.internal:8000/entries

Once the test succeeds, this image is pushed to the public dockerhub repository <br>
`docker push tanvirj9/journal-app:1.1` <br>
The above command is for testing purposes, it will have automated tag increment within the jenkinsfile during pushing to registry.

*NOTE*: Certain changes are done in the `compose.yaml` file (tag name of app is changed for auto version incrementing) after testing. <br/>
### If the above commands work, continue to the next step. 

## 2. Setting up the Kubernetes Manifests for the app and the database.
There are two main deployments, i.e. the app-deployment and the postgres-deployment. The services of both of these deployments are written in the same file for convenience. In addition to these, two configmaps have been defined, 'db-configmap' contains the name of the database that will be used and 'db-init-configMap' contains an initial script that will be run for creating required tables if the database is empty and run for the first time. Lastly, a secrets file, 'db-secret' contains the username, password and the URL of the database that will be used by both the previously mentioned deployments.

The manifests are tested locally in minikube for ensuring proper configuration and if the configurations work properly, we move on to the next step.

## 3. Infrastructure setup
The tool that is used for infrastructure as code is Terraform. Firstly, the VPC is created using module from source `terraform-aws-modules/vpc/aws`. In this setup, three private and three public subnets are used and the subnets are defined in variables whose values are declared in the `terraform.tfvars` file that is not pushed in git. The `eks-cluster.tf` is also created from the module source `terraform-aws-modules/eks/aws` with defined node groups.

The setup is tested locally in the following way:
1. Download the required providers and initialize the workspace:
   ```bash
   terraform init

2. Check and plan the resources that will be created:
   ```bash
   terraform plan

3. Create the resources:
   ```bash
   terraform apply -auto-approve

4. Check the AWS console to see if the desired resources are created. If so, destroy the resources:
   ```bash
   terraform destroy -auto-approve

If the above steps work properly, move on to the next step.
   
## 4. Setting up Jenkins for build, test and deploy
In this project, Jenkins will be run locally within a docker container and to run commands within the pipeline, certain installations need to be performed. 

### Setup Docker within Jenkins continer
The Jenkins container needs to be run with the `docker.sock` file attached from the host machine to the container through volumes. <br/>
1. Docker command for starting the container with attached volumes:
   ```bash
   docker run -p 8080:8080 -p 50000:50000 -d \
    --name jenkins
    -v jenkins_home:/var/jenkins_home \
    -v /var/run/docker.sock:/var/run/docker.sock jenkins/jenkins:lts

2. Next the permissions of the Jenkins container needs to be fixed by entering the container CLI as the root user:
   ```bash
   docker exec -u 0 -it jenkins /bin/bash

3. The permissions need to be fixed in the following way:
   ```bash 
   chmod 666 /var/run/docker.sock

Now the permissions are set properly for Jenkins to run the docker commands within  the pipeline.

### Setup Terraform within Jenkins (running in local docker container)
First install some dependencies before installing Terraform.
1. Login to the container as root user:
   ```bash
   docker exec -u 0 -it jenkins /bin/bash

2. Install the following:
   ```bash
   apt-get update
   apt-get install -y \
   wget \
   curl

3. Install Terraform:
   ```bash
   wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg 
   source /etc/os-release
   CODENAME=$VERSION_CODENAME
   echo "deb [signed-by=/usr/share/keyrings/hashicorp.gpg] \
   https://apt.releases.hashicorp.com $CODENAME main" \
   > /etc/apt/sources.list.d/hashicorp.list
   wget -O- https://apt.releases.hashicorp.com/gpg | \
   gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg
   apt-get install -y terraform

4. Check if the installation was done correctly:
   ```bash
   terraform version

### Install AWS CLI V2
Run the following command for installing AWS CLI V2:
   `curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"`
   `unzip awscliv2.zip && ./aws/install`

Check the installation:
   `aws --version`

### Install kubectl
Run the following command for installing kubectl:
   `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"`
   `chmod +x kubectl && mv kubectl /usr/local/bin/`

As for this project, jenkins is being run locally in docker containers, a tunneling service, ngrok will be setup for exposing local port (like 8080) to a public HTTPS URL.

### Setup ngrok for GitHub’s webhook:
1. Install ngrok:
   ```bash
   sudo apt install snapd
   sudo snap install ngrok

The above commands are run in WSL.

2. Setup webhook in github:
   In github, settings/webhooks, the Jenkins URL should be given in the following format: "https://(path_to_jenkins)/github-webhook/".

   In Jenkins, in settings/CSRF protection, the 'Enable Proxy Compatibility' is enabled for webhooks to access Jenkins.

### Explanation of pipeline
The pipeline automates building, testing, Docker image deployment, infrastructure provisioning using Terraform and Kubernetes deployment.

**Pipeline Overview**
The pipeline consists of four major stages:<br/>

- Build & Test – Builds a Docker image, runs containers, and performs basic API tests.<br/>

- Docker Push – Pushes the built Docker image to Docker Hub.<br/>

- Provisioning – Uses Terraform to provision AWS infrastructure and configure kubeconfig.<br/>

- Deploy – Deploys application resources into an EKS Kubernetes cluster.<br/>

It is triggered automatically when a GitHub push occurs.

1. **Pipeline configuration**
   ```bash
   pipeline {
      agent any
      triggers {
         githubPush()
      }
      environment {
         BUILD_NUMBER = "${env.BUILD_NUMBER}"
   }

*Agent*<br/>
Runs the pipeline on any available Jenkins agent. <br/>

*Trigger*<br/>
`githubPush()` ensures the pipeline is triggered after every push to the connected GitHub repository.<br/>

*Environment Variable*<br/>
`BUILD_NUMBER` stores the Jenkins build number, allowing Docker images to be versioned dynamically.<br/>

2. **Stage: Build & Test**
This stage handles Docker image creation and automated API testing.

*Docker Build*<br/>
Builds the image with a dynamic version:<br/>
`docker build -t tanvirj9/journal-app:1.0.${BUILD_NUMBER} .` <br/>

*Container Startup and Testing* <br/>
Uses Docker Compose to start the application:<br/>
`docker compose -f compose.yaml up -d`<br/>
After waiting for the app to initialize, automated test requests are run:

- POST /entries – Creates a journal entry
- GET /entries – Fetches all entries

If successful, "test successful" is printed.

3. **Stage: Docker Push**
Pushes the newly built versioned Docker image to Docker Hub:<br/>
`docker push tanvirj9/journal-app:1.0.${BUILD_NUMBER}`<br/>

After pushing, the local Docker Compose environment is shut down:<br/>
`docker compose -f compose.yaml down`

4. **Stage: Provisioning**
This stage provisions the AWS infrastructure using Terraform.<br/>

*Credentials*<br/>
The pipeline loads the following sensitive values from Jenkins credentials:

- `AWS_ACCESS_KEY`
- `AWS_SECRET_ACCESS_KEY`

The AWS credentials are set in the environment variables for cloud access. <br/>

*Terraform Commands*<br/>
- `terraform init` initializes Terraform configuration.
- `terraform plan` shows upcoming changes.
- `terraform apply -auto-approve` provisions AWS resources without requiring manual confirmation.

*EKS Configuration*<br/>
After apply, kubeconfig is fetched:<br/>
`aws eks update-kubeconfig --name (name_of_cluster) --region (name_of_region)`<br/>

5. **Stage: Deploy**
Deploys Kubernetes resources into the EKS cluster.<br/>

*Kubernetes Manifests Applied*<br/>
The following files are deployed:
- `db-configMap.yaml`
- `db-init-configMap.yaml`
- `db-secret.yaml`
- `postgres-deployment.yaml`
- `app-deployment.yaml`

*Cluster Verification*<br/>
Commands executed:
- `kubectl get pods – Lists running pods`
- `kubectl get svc app-service – Retrieves the app service details`


*Note: The project is ongoing and the following are going to be implemented:*
- Usage of HashiCorp Vault for handling credentials and secrets management.
- Usage of Prometheus ad Gragana for monitoring and observability.
- Implement security layers.
