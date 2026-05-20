pipeline {
    agent any

    triggers {
        // Run every 5 minutes
        cron('H/10 * * * *')
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    venv/bin/pip install -r requirements.txt --quiet
                '''
            }
        }

        stage('Run GPS Sync') {
            steps {
                sh 'venv/bin/python main.py'
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
