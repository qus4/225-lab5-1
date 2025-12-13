pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        DOCKER_IMAGE = 'cithit/qus4'
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/qus4/225-lab5-1.git'
        KCFG_FILE = credentials('qus4-225')
    }

    stages {

        /* -------------------- CHECKOUT -------------------- */
        stage('Checkout Code') {
            steps {
                cleanWs()
                checkout([$class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: "${GITHUB_URL}"]]
                ])
            }
        }

        /* ------------------- LOAD KUBECONFIG ------------------- */
        stage('Load Kubeconfig') {
            steps {
                withCredentials([file(credentialsId: 'qus4-225', variable: 'KCFG_FILE')]) {
                    sh '''
                        mkdir -p /var/lib/jenkins/.kube
                        cp "$KCFG_FILE" /var/lib/jenkins/.kube/config
                        chmod 600 /var/lib/jenkins/.kube/config
                        echo "[OK] Kubeconfig loaded"
                    '''
                }
            }
        }

        /* ------------------- AUTH TEST ------------------- */
        stage('Test kubectl') {
            steps {
                sh '''
                    kubectl config view
                    kubectl get nodes
                '''
            }
        }

        /* ------------------- BUILD ------------------- */
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

        /* ------------------- DEPLOY DEV ------------------- */
        stage('Deploy to DEV') {
            steps {
                sh """
                    sed -i 's|cithit/qus4:latest|cithit/qus4:${IMAGE_TAG}|g' deployment-dev.yaml
                    kubectl apply -f deployment-dev.yaml
                """
            }
        }

        stage('Wait for DEV Pods') {
            steps {
                sh '''
                    sleep 10
                    kubectl get pods -n default
                '''
            }
        }

        /* ⭐ DEMO PAUSE #1 */
        stage('Pause Demo After DEV Deploy') {
            steps {
                sh '''
                    echo "[DEMO PAUSE] 12s pause for DEV demo"
                    sleep 12
                '''
            }
        }

        /* ------------------- TEST DATA ------------------- */
        stage('Generate Test Data (DEV)') {
            steps {
                sh '''
                    POD=$(kubectl get pods -l app=flask-dev -o jsonpath="{.items[?(@.status.phase=='Running')].metadata.name}")
                    echo "Using POD: $POD"
                    kubectl exec $POD -- python3 data-gen.py
                '''
            }
        }

        /* ⭐ DEMO PAUSE #2 */
        stage('Pause Demo After Data Generation') {
            steps {
                sh '''
                    echo "[DEMO PAUSE] 12s pause to show test data"
                    sleep 12
                '''
            }
        }

        /* ------------------- TESTS ------------------- */
        stage('Acceptance Tests') {
            steps {
                sh "docker build -t qa-tests -f Dockerfile.test ."
            }
        }

        /* ⭐ DEMO PAUSE #3 */
        stage('Pause Demo After Tests') {
            steps {
                sh '''
                    echo "[DEMO PAUSE] 12s pause to show test results"
                    sleep 12
                '''
            }
        }

        /* ------------------- CLEAR TEST DATA ------------------- */
        stage('Clear Test Data') {
            steps {
                sh '''
                    POD=$(kubectl get pods -l app=flask-dev -o jsonpath="{.items[?(@.status.phase=='Running')].metadata.name}")
                    kubectl exec $POD -- python3 data-clear.py
                '''
            }
        }

        /* ⭐ DEMO PAUSE #4 */
        stage('Pause Before PROD Deploy') {
            steps {
                sh '''
                    echo "[DEMO PAUSE] 12s pause before PROD deploy"
                    sleep 12
                '''
            }
        }

        /* ------------------- DEPLOY PROD ------------------- */
        stage('Deploy to PROD') {
            steps {
                sh """
                    sed -i 's|cithit/qus4:latest|cithit/qus4:${IMAGE_TAG}|g' deployment-prod.yaml
                    kubectl apply -f deployment-prod.yaml
                """
            }
        }

        /* ------------------- CLUSTER CHECK ------------------- */
        stage('Check Cluster Resources') {
            steps {
                sh "kubectl get all -n default"
            }
        }
    }

    post {
        success {
            slackSend(color: "good", message: "Build SUCCESS")
        }
        failure {
            slackSend(color: "danger", message: "Build FAILED")
        }
    }
}
