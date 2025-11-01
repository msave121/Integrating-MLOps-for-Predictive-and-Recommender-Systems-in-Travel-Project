pipeline {
    agent any

    environment {
        PYTHON = "C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"
        DOCKER_IMAGE = "msave12345/voyage-analytics-app"
        MODEL_PATH = "model/voyage_model/1/model.pkl"
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/msave121/msave121.git', branch: 'main'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat """
                "%PYTHON%" -m venv .venv
                call .venv\\Scripts\\activate
                "%PYTHON%" -m pip install --upgrade pip
                "%PYTHON%" -m pip install -r requirements.txt
                """
            }
        }

        stage('Run Tests') {
            steps {
                bat """
                call .venv\\Scripts\\activate
                pytest
                """
            }
        }

        stage('Train & Save Model') {
            steps {
                bat """
                call .venv\\Scripts\\activate
                "%PYTHON%" src\\train_regression.py
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                bat "docker build -t %DOCKER_IMAGE% ."
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat """
                    echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin
                    docker push %DOCKER_IMAGE%:latest
                    """
                }
            }
        }
    }

    post {
        success {
            echo '✅ CI/CD Pipeline completed successfully!'
        }
        failure {
            echo '❌ CI/CD Pipeline failed.'
        }
    }
}
