pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        DOCKER_IMAGE = 'cithit/qus4'
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/qus4/225-lab5-1.git'
        KUBECONFIG_CRED = 'qus4-225'
    }

    stages {

        stage('Checkout Code') {
            steps {
                cleanWs()
                checkout scm
            }
        }

        stage('Load Kubeconfig') {
            steps {
                withCredentials([file(credentialsId: "${KUBECONFIG_CRED}", variable: 'KCFG')]) {
                    sh """
                        mkdir -p ~/.kube
                        cp \$KCFG ~/.kube/config
                        chmod 600 ~/.kube/config
                        echo 'Kubeconfig Loaded'
                    """
                }
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
                sh "sed -i 's|cithit/qus4:latest|cithit/qus4:${IMAGE_TAG}|' deployment-dev.yaml"
                sh "kubectl apply -f deployment-dev.yaml"
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
                    def pod = sh(
                        script: "kubectl get pods -l app=flask-dev -o jsonpath='{.items[0].metadata.name}'",
                        returnStdout: true
                    ).trim()
                    sh "kubectl exec ${pod} -- python3 data-gen.py"
                }
            }
        }

        stage('Acceptance Tests') {
            steps {
                sh "docker build -t qa-tests -f Dockerfile.test ."
            }
        }

        stage('Clear Test Data') {
            steps {
                script {
                    def pod = sh(
                        script: "kubectl get pods -l app=flask-dev -o jsonpath='{.items[0].metadata.name}'",
                        returnStdout: true
                    ).trim()
                    sh "kubectl exec ${pod} -- python3 data-clear.py"
                }
            }
        }

        stage('Deploy to PROD') {
            steps {
                sh "sed -i 's|cithit/qus4:latest|cithit/qus4:${IMAGE_TAG}|' deployment-prod.yaml"
                sh "kubectl apply -f deployment-prod.yaml"
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
