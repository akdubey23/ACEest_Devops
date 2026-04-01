// ACEest Fitness API — simple CI-style pipeline for coursework
// Prereqs on the Jenkins agent: Git, Python 3, pip, Docker (for the final stage)

pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Uses the repository configured on the Jenkins job (Multibranch / Pipeline from SCM)
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh 'python3 -m pip install --upgrade pip'
                sh 'python3 -m pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                sh 'python3 -m pytest tests/ -v --tb=short'
            }
        }

        stage('Docker build') {
            steps {
                sh 'docker build -t aceest-fitness-api:jenkins .'
            }
        }
    }
}
