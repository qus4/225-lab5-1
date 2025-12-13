pipeline {
    agent any

    environment {
        KCFG = credentials('qus4-225')   // <-- 这里保持不变
    }

    stages {

        stage('Load Kubeconfig') {
            steps {
                sh '''
                    mkdir -p $HOME/.kube
                    cp "$KCFG" $HOME/.kube/config
                    chmod 600 $HOME/.kube/config
                    echo "Kubeconfig Loaded"
                '''
            }
        }

        stage('Test kubectl auth') {
            steps {
                sh '''
                    echo "Testing kubectl authentication..."
                    kubectl config view
                    kubectl get pods --all-namespaces
                '''
            }
        }

    }

    post {
        success {
            echo "Kubeconfig works! Authentication SUCCESS."
        }
        failure {
            echo "Kubeconfig FAILED. Authentication error."
        }
    }
}
