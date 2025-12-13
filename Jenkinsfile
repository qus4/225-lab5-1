pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        DOCKER_IMAGE = 'cithit/qus4'                   // your MiamiID
        GITHUB_URL = 'https://github.com/qus4/225-lab5-1.git'
        KUBECONFIG = credentials('qus4-225')
    }

    stages {

        stage('Checkout Code') {
            steps {
                cleanWs()
                checkout([$class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: "${GITHUB_URL}"]]
                ])
            }
        }

        stage('Static Code Test (flake8)') {
            steps {
                sh 'pip install flake8'
                sh 'flake8 *.py'
            }
        }

        stage('Build & Push DEV Image') {
            steps {
                script {
                    docker.withRegistry("https://registry.hub.docker.com", "${DOCKER_CREDENTIALS_ID}") {
                        sh "docker build -t ${DOCKER_IMAGE}:dev -f Dockerfile.build ."
                        sh "docker push ${DOCKER_IMAGE}:dev"
                    }
                }
            }
        }

        stage('Deploy to DEV') {
            steps {
                script {
                    sh "sed -i 's|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:dev|' deployment-dev.yaml"
                    sh "kubectl apply -f deployment-dev.yaml"
                    sh "kubectl apply -f service-dev.yaml || true"
                }
            }
        }

        stage('Wait for DEV Pods') {
            steps {
                sh "sleep 20"
                sh "kubectl get pods"
            }
        }

        stage("Generate Test Data") {
            steps {
                script {
                    def podName = sh(script: "kubectl get pods -l app=flask-dev -o jsonpath='{.items[0].metadata.name}'", returnStdout: true).trim()
                    sh "kubectl exec ${podName} -- python3 data-gen.py"
                }
            }
        }

        stage("Run Acceptance Tests") {
            steps {
                script {
                    sh "docker build -t test-runner -f Dockerfile.test ."
                    sh "docker run test-runner"
                }
            }
        }

        stage("Clear Test Data (DEV)") {
            steps {
                script {
                    def podName = sh(script: "kubectl get pods -l app=flask-dev -o jsonpath='{.items[0].metadata.name}'", returnStdout: true).trim()
                    sh "kubectl exec ${podName} -- python3 data-clear.py"
                }
            }
        }

        stage('Build & Push PROD Image') {
            steps {
                script {
                    docker.withRegistry("https://registry.hub.docker.com", "${DOCKER_CREDENTIALS_ID}") {
                        sh "docker build -t ${DOCKER_IMAGE}:prod -f Dockerfile.build ."
                        sh "docker push ${DOCKER_IMAGE}:prod"
                    }
                }
            }
        }

        stage('Deploy to PROD') {
            steps {
                script {
                    sh "sed -i 's|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:prod|' deployment-prod.yaml"
                    sh "kubectl apply -f deployment-prod.yaml"
                    sh "kubectl apply -f service-prod.yaml || true"
                }
            }
        }

        stage("Check Cluster Resources") {
            steps {
                sh "kubectl get all"
            }
        }
    }

    post {
        success {
            slackSend color: "good", message: "Build SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
        failure {
            slackSend color: "danger", message: "Build FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
    }
}
