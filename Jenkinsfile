pipeline {
    agent any

    environment {
        PATH = "C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python314;${PATH}"
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/msave121/msave121.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m venv .venv'
                bat 'call .venv\\Scripts\\activate && python -m pip install --upgrade pip'
                bat 'call .venv\\Scripts\\activate && pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'call .venv\\Scripts\\activate && pytest tests/'
            }
        }

        stage('Train & Save Model') {
            steps {
                bat 'call .venv\\Scripts\\activate && python src/train_regression.py --users data/users.csv --flights data/flights.csv --hotels data/hotels.csv'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t voyage-analytics-app .'
            }
        }

        stage('Push Docker Image') {
            steps {
                echo "Skipping Docker push for local build"
            }
        }

        stage('Post Actions') {
            steps {
                echo "✅ CI/CD Pipeline completed successfully."
            }
        }
    }

    post {
        failure {
            echo "❌ CI/CD Pipeline failed."
        }
    }
}
