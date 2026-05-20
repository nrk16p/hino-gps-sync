pipeline {
    agent any

    triggers {
        // Run every 5 minutes
        cron('H/10 * * * *')
    }

    environment {
        PYTHON = 'python3'
    }

    stages {
        stage('Setup') {
            steps {
                sh '${PYTHON} -m pip install -r requirements.txt --quiet'
            }
        }

        stage('Run GPS Sync') {
            steps {
                sh '${PYTHON} main.py'
            }
        }
    }

    post {
        success {
            echo '✅ Hino GPS sync completed successfully'
        }
        failure {
            echo '❌ Hino GPS sync failed'
        }
    }
}
