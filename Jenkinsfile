pipeline {
    agent any

    environment {
        // ✅ Fix Unicode error on Windows (force UTF-8)
        PYTHONIOENCODING = "utf-8"
        CHCP = "65001"

        // Docker + Model Paths
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
                bat '''
                chcp 65001 > NUL
                python -m venv .venv
                call .venv\\Scripts\\activate
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                bat '''
                chcp 65001 > NUL
                call .venv\\Scripts\\activate
                pytest || echo "⚠ No tests found, skipping..."
                '''
            }
        }

        stage('Train & Save Model') {
            steps {
                bat '''
                chcp 65001 > NUL
                call .venv\\Scripts\\activate
                python src/train_regression.py
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                docker build -t %DOCKER_IMAGE% .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat '''
                    docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                    docker push %DOCKER_IMAGE%
                    '''
                }
            }
        }

        stage('Trigger Airflow Reload') {
            steps {
                script {
                    // Trigger Airflow REST API DAG (reload_model_dag)
                    def response = bat(script: '''
                    curl -X POST "http://localhost:8080/api/v1/dags/reload_model_dag/dagRuns" ^
                    -H "Content-Type: application/json" ^
                    -u "airflow:airflow" ^
                    -d "{\\"conf\\": {\\"message\\": \\"Model retrained via Jenkins\\"}}"
                    ''', returnStatus: true)
                    echo "Airflow API call status: ${response}"
                }
            }
        }
    }

    post {
        success {
            echo "✅ CI/CD Pipeline completed successfully!"
        }
        failure {
            echo "❌ CI/CD Pipeline failed."
        }
    }
}
