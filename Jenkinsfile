pipeline {
  agent any

  options { timestamps() }

  environment {
    // Prefer a system-wide Python install path that actually exists for the Jenkins service user
    PY_HOME = 'C:\\Python313'  // <- change to your real path (folder containing python.exe)
    PATH = "${PY_HOME};${PATH}"
  }

  stages {
    stage('Checkout') {
      steps {
        // Pin the branch to main to avoid the "couldn't find any revision" error
        git branch: 'main',
            url: 'https://github.com/msave121/msave121.git'
      }
    }

    stage('Install Dependencies') {
      steps {
        bat '''
          python --version
          python -m venv .venv
          call .venv\\Scripts\\activate && python -m pip install --upgrade pip
          call .venv\\Scripts\\activate && pip install -r requirements.txt
        '''
      }
    }

    stage('Run Tests') {
      steps {
        bat 'call .venv\\Scripts\\activate && pytest -q tests'
      }
    }

    stage('Train & Save Model') {
      steps {
        bat 'call .venv\\Scripts\\activate && python src/train_regression.py --users data/users.csv --flights data/flights.csv --hotels data/hotels.csv'
      }
    }

    stage('Build Docker Image') {
      when { expression { return fileExists('Dockerfile') } }
      steps {
        bat 'docker --version'
        bat 'docker build -t voyage-analytics-app .'
      }
    }

    stage('Push Docker Image') {
      steps {
        echo 'Skipping Docker push for local build'
      }
    }

    stage('Post Actions') {
      steps {
        echo '✅ CI/CD Pipeline completed successfully.'
      }
    }
  }

  post {
    failure { echo '❌ CI/CD Pipeline failed.' }
  }
}
