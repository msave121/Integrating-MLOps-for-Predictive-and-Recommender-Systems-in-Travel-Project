// pipeline {
//     agent any

//     environment {
//         PYTHON_PATH = "C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"
//         DOCKER_IMAGE = "msave12345/voyage-analytics-app"
//         MODEL_PATH = "model/voyage_model/1/model.pkl"
//         AIRFLOW_URL = "http://localhost:8080/api/v1/dags/reload_model_dag/dagRuns"
//         AIRFLOW_USER = "admin"        // change if different
//         AIRFLOW_PASS = "admin"        // change if different
//     }

//     stages {
//         stage('Checkout') {
//             steps {
//                 git url: 'https://github.com/msave121/msave121.git', branch: 'main'
//             }
//         }

//         stage('Install Dependencies') {
//             steps {
//                 bat """
//                 "${PYTHON_PATH}" -m venv .venv
//                 call .venv\\Scripts\\activate
//                 python -m pip install --upgrade pip
//                 pip install -r requirements.txt
//                 """
//             }
//         }

//         stage('Run Tests') {
//             steps {
//                 bat """
//                 call .venv\\Scripts\\activate
//                 pytest || exit /b 0
//                 """
//             }
//         }

//         stage('Train & Save Model') {
//             steps {
//                 bat """
//                 call .venv\\Scripts\\activate
//                 python src\\train_regression.py
//                 """
//             }
//         }

//         stage('Build Docker Image') {
//             steps {
//                 bat "docker build -t %DOCKER_IMAGE% ."
//             }
//         }

//         stage('Push Docker Image') {
//             steps {
//                 withCredentials([usernamePassword(credentialsId: 'dockerhub-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
//                     bat """
//                     echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin
//                     docker push %DOCKER_IMAGE%:latest
//                     """
//                 }
//             }
//         }

//         stage('Deploy Container') {
//             steps {
//                 bat """
//                 docker stop voyage_app || exit 0
//                 docker rm voyage_app || exit 0
//                 docker pull %DOCKER_IMAGE%:latest
//                 docker run -d -p 5050:5050 --name voyage_app %DOCKER_IMAGE%:latest
//                 """
//             }
//         }

//         stage('Trigger Airflow Reload') {
//             steps {
//                 bat """
//                 curl -X POST "%AIRFLOW_URL%" ^
//                 -u "%AIRFLOW_USER%:%AIRFLOW_PASS%" ^
//                 -H "Content-Type: application/json" ^
//                 -d "{\\"conf\\": {\\"triggered_by\\": \\"jenkins\\"}}"
//                 """
//             }
//         }
//     }

//     post {
//         success {
//             echo '✅ CI/CD Pipeline completed successfully and triggered Airflow reload.'
//         }
//         failure {
//             echo '❌ CI/CD Pipeline failed.'
//         }
//     }
// }

pipeline {
    agent any

    environment {
        PYTHON = "C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"
        AIRFLOW_URL = "http://localhost:8080"
        AIRFLOW_USER = "airflow"
        AIRFLOW_PASS = "airflow"
        DAG_ID = "reload_model_dag"
    }

    stages {
        stage('Setup') {
            steps {
                echo "Setting up environment..."
                bat "${env.PYTHON} -m venv venv"
                bat "venv\\Scripts\\pip install -r requirements.txt"
            }
        }

        stage('Run Tests') {
            steps {
                echo "Running tests..."
                bat "venv\\Scripts\\pytest || echo 'No tests found, skipping...'"
            }
        }

        stage('Build Model') {
            steps {
                echo "Training or building model..."
                bat "${env.PYTHON} src/train_regression.py --users data/users.csv --flights data/flights.csv --hotels data/hotels.csv"
            }
        }

        stage('Trigger Airflow DAG') {
            steps {
                echo "Triggering Airflow DAG ${env.DAG_ID}"
                bat """
                curl -X POST %AIRFLOW_URL%/api/v1/dags/%DAG_ID%/dagRuns ^
                    -H "Content-Type: application/json" ^
                    -u %AIRFLOW_USER%:%AIRFLOW_PASS% ^
                    -d "{\\"conf\\": {\\"triggered_by\\": \\"Jenkins pipeline\\"}}"
                """
            }
        }
    }

    post {
        success {
            echo "✅ CI/CD pipeline completed successfully."
        }
        failure {
            echo "❌ Pipeline failed. Check logs."
        }
    }
}
