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

        /* ------------------------- CHECKOUT ------------------------- */
        stage('Checkout Code') {
            steps {
                cleanWs()
                checkout([$class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: "${GITHUB_URL}"]]
                ])
            }
        }

        /* --------------------- LOAD KUBECONFIG ---------------------- */
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

        /* --------------------- AUTH TEST ---------------------------- */
        stage('Test kubectl') {
            steps {
                sh '''
                    echo "[TEST] kubectl config view"
                    kubectl config view

                    echo "[TEST] kubectl get nodes"
                    kubectl get nodes
                '''
            }
        }

        /* ------------------------- BUILD ---------------------------- */
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

        /* ------------------------ DEV DEPLOY ------------------------ */
        stage('Deploy to DEV') {
            steps {
                sh """
                    sed -i 's|cithit/qus4:latest|cithit/qus4:${IMAGE_TAG}|g' deployment-dev.yaml
                    kubectl apply -f deployment-dev.yaml
                """
            }
        }

        /* ------------------------ WAIT DEV -------------------------- */
        stage('Wait for DEV Pods') {
            steps {
                sh '''
                    echo "[INFO] Waiting for DEV pod to start..."
                    sleep 12
                    kubectl get pods -n default
                '''
            }
        }

        /* ---------------------- GENERATE DATA ----------------------- */
        stage('Generate Test Data (DEV)') {
            steps {
                sh '''
                    POD=$(kubectl get pods -l app=flask-dev -o jsonpath="{.items[?(@.status.phase=='Running')].metadata.name}")
                    echo "Using POD: $POD"
                    kubectl exec $POD -- python3 data-gen.py
                    sleep 5
                '''
            }
        }

        /* ------------------------ TESTS ----------------------------- */
        stage('Acceptance Tests') {
            steps {
                sh "docker build -t qa-tests -f Dockerfile.test ."
                sh "echo '[INFO] Test container built successfully'"
                sleep 5
            }
        }

        /* ------------------------ CLEAR DATA ------------------------ */
        stage('Clear Test Data') {
            steps {
                sh '''
                    POD=$(kubectl get pods -l app=flask-dev -o jsonpath="{.items[?(@.status.phase=='Running')].metadata.name}")
                    echo "Using POD: $POD"
                    kubectl exec $POD -- python3 data-clear.py
                    sleep 5
                '''
            }
        }

        /* ------------------------ PROD DEPLOY ----------------------- */
        stage('Deploy to PROD') {
            steps {
                sh """
                    sed -i 's|cithit/qus4:latest|cithit/qus4:${IMAGE_TAG}|g' deployment-prod.yaml
                    kubectl apply -f deployment-prod.yaml
                    echo '[INFO] Waiting for PROD to update...'
                    sleep 10
                """
            }
        }

        /* -------------------- CLUSTER RESOURCES --------------------- */
        stage('Check Cluster Resources') {
            steps {
                sh '''
                    echo "[INFO] Checking cluster resources..."
                    kubectl get all -n default
                '''
            }
        }
    }

    /* -------------------------- POST ------------------------------ */
    post {
        success {
            slackSend(color: "good", message: "Build SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        failure {
            slackSend(color: "danger", message: "Build FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
    }
}

