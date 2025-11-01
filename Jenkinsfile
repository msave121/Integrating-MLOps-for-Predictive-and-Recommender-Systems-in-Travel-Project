pipeline {
  agent any

  options { timestamps() }

  environment {
    // System Python used only to CREATE the venv
    PYTHON = 'C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'
    DOCKER_IMAGE = 'msave12345/voyage-analytics-app:latest'
    VENV_PY = '.\\.venv\\Scripts\\python'
    VENV_PIP = '.\\.venv\\Scripts\\python -m pip'
    PIP_DISABLE_PIP_VERSION_CHECK = '1'
    PIP_NO_INPUT = '1'
    PYTHONUTF8 = '1'
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
          "%PYTHON%" -m venv .venv
          %VENV_PY% -m pip install --upgrade pip wheel
          %VENV_PIP% install -r requirements.txt
        '''
      }
    }

    stage('Run Tests') {
      steps {
        bat '%VENV_PY% -m pytest -q tests || %VENV_PY% -m pytest -q'
      }
    }

    stage('Train & Save Model') {
      steps {
        bat '%VENV_PY% src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv'
      }
    }

    stage('Build Docker Image') {
      steps {
        bat '''
          where docker >nul 2>&1
          if %ERRORLEVEL% NEQ 0 (
            echo Docker not found on this agent. Skipping Docker build.
          ) else (
            docker build -t %DOCKER_IMAGE% .
          )
        '''
      }
    }

    stage('Push Docker Image') {
      when {
        expression { return true } // set a condition if you want (e.g., only on main)
      }
      steps {
        bat '''
          where docker >nul 2>&1
          if %ERRORLEVEL% NEQ 0 (
            echo Docker not found; skipping push.
            exit /b 0
          )
        '''
        withCredentials([usernamePassword(credentialsId: 'dockerhub-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          bat '''
            echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin
            docker push %DOCKER_IMAGE%
          '''
        }
      }
    }
  }

  post {
    success { echo '✅ CI/CD Pipeline completed successfully!' }
    failure { echo '❌ CI/CD Pipeline failed.' }
  }
}
