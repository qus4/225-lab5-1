pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        DOCKER_IMAGE = 'cithit/qus4'                
        IMAGE_TAG = "build-${BUILD_NUMBER}"
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
                sh "pip install flake8"
                sh "flake8 . || true"
            }
        }

        stage('Build & Push DEV Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIALS_ID) {
                        sh "docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} -f Dockerfile.build ."
                        sh "docker push ${DOCKER_IMAGE}:${IMAGE_TAG}"
                    }
                }
            }
        }

        stage('Deploy to DEV') {
            steps {
                script {
                    sh "sed -i 's|cithit/qus4:latest|cithit/qus4:${IMAGE_TAG}|' deployment-dev.yaml"
                    sh "kubectl apply -f deployment-dev.yaml"
                }
            }
        }

        stage('Wait for DEV Pods') {
            steps {
                sh "sleep 10"
                sh "kubectl get pods"
            }
        }

        stage('Generate Test Data (DEV)') {
            steps {
                script {
                    sh "sleep 5"
                    def pod = sh(script: \"kubectl get pods -l app=flask-dev -o jsonpath='{.items[0].metadata.name}'\", returnStdout: true).trim()
                    sh "kubectl exec ${pod} -- python3 data-gen.py"
                }
            }
        }

        stage('Run Acceptance Tests') {
            steps {
                sh "docker build -t qa-tests -f Dockerfile.test ."
            }
        }

        stage('Clear Test Data (DEV)') {
            steps {
                script {
                    def pod = sh(script: \"kubectl get pods -l app=flask-dev -o jsonpath='{.items[0].metadata.name}'\", returnStdout: true).trim()
                    sh "kubectl exec ${pod} -- python3 data-clear.py"
                }
            }
        }

        stage('Deploy to PROD') {
            steps {
                script {
                    sh "sed -i 's|cithit/qus4:latest|cithit/qus4:${IMAGE_TAG}|' deployment-prod.yaml"
                    sh "kubectl apply -f deployment-prod.yaml"
                }
            }
        }

        stage('Check Cluster Resources') {
            steps {
                sh "kubectl get all"
            }
        }
    }

    post {
        success {
            slackSend(color: "good", message: "Build Success: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        failure {
            slackSend(color: "danger", message: "Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
    }
}
