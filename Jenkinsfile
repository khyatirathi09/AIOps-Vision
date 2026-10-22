pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Train and Validate Model') {
            steps {
                bat 'python train_model.py'
            }
        }

        stage('Automated Tests') {
            steps {
                bat 'python -m pytest -q'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t aiops-vision:latest .'
            }
        }
    }

    post {
        success {
            echo 'AIOps Vision CI pipeline completed successfully.'
            archiveArtifacts artifacts: 'models/model_metadata.json', fingerprint: true
        }
        failure {
            echo 'Pipeline failed. Review the stage logs and fix the issue.'
        }
    }
}
