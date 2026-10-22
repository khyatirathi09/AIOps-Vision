
pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\Lenovo\\AppData\\Local\\Python\\bin\\python.exe'
    }

    stages {
        stage('Check Python') {
            steps {
                bat '"%PYTHON%" --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install -r requirements.txt'
            }
        }

        stage('Train AI Model') {
            steps {
                bat '"%PYTHON%" train_model.py'
            }
        }

        stage('Run Automated Tests') {
            steps {
                bat '"%PYTHON%" -m pytest -v'
            }
        }
    }

    post {
        success {
            echo 'AIOps Vision pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the Console Output.'
        }
    }
}
