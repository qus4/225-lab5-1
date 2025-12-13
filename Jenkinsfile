pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        DOCKER_IMAGE = 'cithit/qus4'
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/qus4/225-lab5-1.git'
        KCFG = credentials('qus4-225')    // <-- your kubeconfig file
    }

    stages {

        /* ---------------------------
         * 1. Checkout GitHub Source Code
         * --------------------------- */
        stage('Checkout Code') {
            steps {
                cleanWs()
                checkout([$class: 'GitSCM',
                  branches: [[name: '*/main']],
                  userRemoteConfigs: [[url: "${GITHUB_URL}"]]
                ])
            }
        }

        /* ---------------------------
         * 2. Load kubeconfig to Jenkins
         * --------------------------- */
        stage('Load Kubeconfig') {
            steps {
                withCredentials([file(credentialsId: 'qus4-225', variable: 'KCFG_FILE')]) {
                    sh '''
                        mkdir -p ~/.kube
                        cp "$KCFG_FILE" ~/.kube/config
                        chmod 600 ~/.kube/config
                        echo "[OK] Kubeconfig loaded"
                    '''
                }
            }
        }

        /* ---------------------------
         * 3. Test kubectl Authentication
         * --------------------------- */
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

        /* ---------------------------
         * 4. Build & Push DEV Image
         * --------------------------- */
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

        /* ---------------------------
         * 5. Deploy to DEV namespace
         * --------------------------- */
        stage('Deploy to DEV') {
            steps {
                sh '''
                    sed -i "s|cithit/qus4:latest|cithit/qus4:'"${IMAGE_TAG}"'|" deployment-dev.yaml
                    kubectl apply -f deployment-dev.yaml
                '''
            }
        }

        /* ---------------------------
         * 6. Wait for DEV Pods
         * --------------------------- */
        stage('Wait for DEV Pods') {
            steps {
                sh '''
                    sleep 10
                    kubectl get pods -n default
                '''
            }
        }

        /* ---------------------------
         * 7. Generate Test Data in DEV
         * --------------------------- */
        stage('Generate Test Data (DEV)') {
            steps {
                script {
                    def pod = sh(
                      script: "kubectl get pods -l app=flask-dev -o jsonpath='{.items[0].metadata.name}'",
                      returnStdout: true
                    ).trim()

                    sh "kubectl exec ${pod} -- python3 data-gen.py"
                }
            }
        }

        /* ---------------------------
         * 8. Run Acceptance Tests (requests-based)
         * --------------------------- */
        stage('Acceptance Tests') {
            steps {
                sh '''
                    docker build -t qa-tests -f Dockerfile.test .
                    docker run --rm qa-tests
                '''
            }
        }

        /* ---------------------------
         * 9. Clear test data after testing
         * --------------------------- */
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

        /* ---------------------------
         * 10. Deploy to PROD environment
         * --------------------------- */
        stage('Deploy to PROD') {
            steps {
                sh '''
                    sed -i "s|cithit/qus4:latest|cithit/qus4:'"${IMAGE_TAG}"'|" deployment-prod.yaml
                    kubectl apply -f deployment-prod.yaml
                '''
            }
        }

        /* ---------------------------
         * 11. Check Production Status
         * --------------------------- */
        stage('Check Cluster Resources') {
            steps {
                sh 'kubectl get all -n default'
            }
        }

    } // end stages

    /* ---------------------------
     * POST actions
     * --------------------------- */
    post {
        success {
            slackSend(color: "good", message: "Build SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        failure {
            slackSend(color: "danger", message: "Build FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
    }

}
