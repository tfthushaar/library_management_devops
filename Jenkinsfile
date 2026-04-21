pipeline {
  agent any

  parameters {
    string(name: 'AWS_REGION', defaultValue: 'ap-south-1', description: 'AWS region for the ALB, EC2 instances, and CloudWatch resources.')
    string(name: 'ALB_LISTENER_ARN', defaultValue: '', description: 'Terraform output: listener_arn')
    string(name: 'BLUE_TARGET_GROUP_ARN', defaultValue: '', description: 'Terraform output: blue_target_group_arn')
    string(name: 'GREEN_TARGET_GROUP_ARN', defaultValue: '', description: 'Terraform output: green_target_group_arn')
    string(name: 'ALB_DNS_NAME', defaultValue: '', description: 'Terraform output: alb_dns_name')
    string(name: 'ANSIBLE_PRIVATE_KEY_FILE', defaultValue: '/var/lib/jenkins/.ssh/library-bluegreen.pem', description: 'Private key path on the Jenkins agent.')
  }

  environment {
    AWS_DEFAULT_REGION = "${params.AWS_REGION}"
    ALB_LISTENER_ARN = "${params.ALB_LISTENER_ARN}"
    BLUE_TARGET_GROUP_ARN = "${params.BLUE_TARGET_GROUP_ARN}"
    GREEN_TARGET_GROUP_ARN = "${params.GREEN_TARGET_GROUP_ARN}"
    ALB_DNS_NAME = "${params.ALB_DNS_NAME}"
    ANSIBLE_PRIVATE_KEY_FILE = "${params.ANSIBLE_PRIVATE_KEY_FILE}"
    VENV_DIR = '.venv'
  }

  options {
    timestamps()
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build') {
      steps {
        sh '''
          python3 -m venv ${VENV_DIR}
          . ${VENV_DIR}/bin/activate
          pip install --upgrade pip
          pip install -r app/requirements.txt
        '''
      }
    }

    stage('Test') {
      steps {
        sh '''
          . ${VENV_DIR}/bin/activate
          PYTHONPATH=app pytest -q app/tests --junitxml=pytest.xml
        '''
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: '**/pytest.xml'
        }
      }
    }

    stage('Security Testing Stage') {
      steps {
        sh '''
          . ${VENV_DIR}/bin/activate
          cd app
          nohup ../${VENV_DIR}/bin/gunicorn --workers 2 --bind 127.0.0.1:5001 wsgi:app > ../gunicorn-local.log 2>&1 &
          echo $! > ../gunicorn-local.pid
          sleep 8
          cd ..
          chmod +x jenkins/scripts/run_zap_baseline.sh
          jenkins/scripts/run_zap_baseline.sh http://127.0.0.1:5001
        '''
      }
      post {
        always {
          sh '''
            if [ -f gunicorn-local.pid ]; then
              kill $(cat gunicorn-local.pid) || true
              rm -f gunicorn-local.pid
            fi
          '''
          archiveArtifacts artifacts: 'zap-report.html,gunicorn-local.log', allowEmptyArchive: true
        }
      }
    }

    stage('Deploy to Green') {
      steps {
        sh '''
          test -n "${ANSIBLE_PRIVATE_KEY_FILE}"
          export ANSIBLE_HOST_KEY_CHECKING=False
          ansible-playbook -i ansible/inventory/inventory.ini ansible/playbooks/deploy_app.yml --limit green
        '''
      }
    }

    stage('Verify Green') {
      steps {
        sh '''
          chmod +x jenkins/scripts/verify_green.sh
          jenkins/scripts/verify_green.sh ansible/inventory/inventory.ini
        '''
      }
    }

    stage('Switch Traffic') {
      steps {
        sh '''
          test -n "${ALB_LISTENER_ARN}"
          test -n "${GREEN_TARGET_GROUP_ARN}"
          chmod +x jenkins/scripts/switch_traffic.sh
          jenkins/scripts/switch_traffic.sh
        '''
      }
    }

    stage('Rollback to Blue if verification fails') {
      steps {
        sh '''
          test -n "${ALB_DNS_NAME}"
          chmod +x jenkins/scripts/rollback_blue.sh

          echo "Running post-switch ALB health check..."
          sleep 15
          curl --fail --silent --show-error http://${ALB_DNS_NAME}/health > /tmp/alb-health.json || (
            echo "Post-switch validation failed. Rolling back to blue target group."
            jenkins/scripts/rollback_blue.sh
            exit 1
          )
          cat /tmp/alb-health.json
        '''
      }
    }
  }

  post {
    failure {
      echo 'Pipeline failed. Review the stage logs, verification output, and OWASP ZAP report.'
    }
    success {
      echo 'Blue-green deployment for the library management portal completed successfully.'
    }
  }
}
