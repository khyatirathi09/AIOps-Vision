
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
                    if errorlevel 1 exit /b 1

                    "%DOCKER%" rm aiops-vision
                    if errorlevel 1 exit /b 1

                    "%DOCKER%" run -d --name aiops-vision --restart unless-stopped -p 5000:5000 %IMAGE_NAME%:%BUILD_NUMBER%
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    sleep(time: 10, unit: 'SECONDS')
                }

                bat '"%DOCKER%" ps --filter name=aiops-vision'

                bat '''
                    "%DOCKER%" inspect --format="{{.State.Running}}" aiops-vision > container_status.txt
                    if errorlevel 1 exit /b 1
                    findstr /i "true" container_status.txt
                    if errorlevel 1 exit /b 1
                '''

                bat '"%DOCKER%" logs --tail 30 aiops-vision'
            }
        }
    }

    post {
        success {
            echo 'AIOps Vision CI/CD pipeline completed successfully!'
            echo 'Model training and automated tests passed.'
            echo 'Docker image built and container deployment verified.'
            echo 'Dashboard URL: http://localhost:5000'
        }

        failure {
            echo 'Pipeline failed. Check the failed stage in Console Output.'
            echo 'Check Docker logs if the container failed to start.'
        }
    }
}
