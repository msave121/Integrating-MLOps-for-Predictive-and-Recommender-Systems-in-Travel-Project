pipeline {
    agent any

    environment {
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
                sh '''
                python -m venv .venv
                source .venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                source .venv/bin/activate
                pytest
                '''
            }
        }

        stage('Train & Save Model') {
            steps {
                sh '''
                source .venv/bin/activate
                python src/train_regression.py
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t $DOCKER_IMAGE ."
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    docker push $DOCKER_IMAGE:latest
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline completed successfully'
        }
        failure {
            echo 'CI/CD Pipeline failed'
        }
    }
}
