pipeline {
    agent any

    environment {
        VENV_DIR = ".venv"
        DOCKER_IMAGE = "voyage-analytics-app:latest"
        AIRFLOW_API = "http://localhost:8080/api/v1/dags/reload_model_dag/dagRuns"
    }

    stages {

        stage('🧹 Cleanup Workspace') {
            steps {
                echo 'Cleaning old virtual environment...'
                bat '''
                IF EXIST %VENV_DIR% (
                    rmdir /S /Q %VENV_DIR%
                )
                '''
            }
        }

        stage('📦 Install Dependencies') {
            steps {
                echo 'Setting up Python virtual environment...'
                bat '''
                python -m venv %VENV_DIR%
                call %VENV_DIR%\\Scripts\\activate
                pip install --upgrade pip
                pip install --no-cache-dir -r requirements.txt
                '''
            }
        }

        stage('✅ Run Tests') {
            steps {
                echo 'Running tests...'
                bat '''
                call %VENV_DIR%\\Scripts\\activate
                pytest --maxfail=1 --disable-warnings -q
                '''
            }
        }

        stage('🤖 Train & Save Model') {
            steps {
                echo 'Training and saving ML model...'
                bat '''
                call %VENV_DIR%\\Scripts\\activate
                python src\\train_regression.py
                '''
            }
        }

        stage('🐳 Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                bat '''
                docker build -t %DOCKER_IMAGE% .
                '''
            }
        }

        stage('🚀 Trigger Airflow Reload') {
            when {
                expression { return true }  // set to false if you want to skip
            }
            steps {
                echo 'Triggering Airflow DAG reload...'
                bat '''
                curl -X POST %AIRFLOW_API% ^
                    -H "Content-Type: application/json" ^
                    -u "airflow:airflow" ^
                    -d "{}"
                '''
            }
        }
    }

    post {
        success {
            echo "✅ CI/CD pipeline completed successfully!"
        }
        failure {
            echo "❌ CI/CD Pipeline failed."
        }
    }
}
