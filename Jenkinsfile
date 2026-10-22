
pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\Lenovo\\AppData\\Local\\Python\\bin\\python.exe'
        DOCKER = 'C:\\Users\\Lenovo\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        IMAGE_NAME = 'aiops-vision'
    }

    stages {
        stage('Check Python') {
            steps {
                bat '"%PYTHON%" --version'
            }
        }

        stage('Check Docker Access') {
            steps {
                bat '"%DOCKER%" --version'
                bat '"%DOCKER%" info'
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

        stage('Build Docker Image') {
            steps {
                bat '"%DOCKER%" build -t %IMAGE_NAME%:%BUILD_NUMBER% .'
            }
        }

        stage('Deploy Docker Container') {
            steps {
                bat '''
                    "%DOCKER%" stop aiops-vision
                    "%DOCKER%" rm aiops-vision
                    "%DOCKER%" run -d --name aiops-vision --restart unless-stopped -p 5000:5000 %IMAGE_NAME%:%BUILD_NUMBER%
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                bat 'timeout /t 10 /nobreak'
                bat '"%DOCKER%" ps --filter name=aiops-vision'
                bat '"%DOCKER%" logs --tail 30 aiops-vision'
            }
        }
    }

    post {
        success {
            echo 'AIOps Vision CI/CD pipeline completed successfully!'
            echo 'Docker image built and container deployed.'
        }
        failure {
            echo 'Pipeline failed. Check Console Output and Docker logs.'
        }
    }
}
