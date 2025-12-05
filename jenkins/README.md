# Jenkins CI/CD Pipelines

Four Jenkins pipelines for automated deployment to EKS.

## Pipeline Overview

### 0. Setup Pipeline (Jenkinsfile-setup)
**Purpose:** Configure kubectl context on Jenkins EC2  
**Agent:** Jenkins EC2 (`agent any`)  
**When to run:** Once per environment or when switching between dev/prod  
**What it does:** Runs `aws eks update-kubeconfig --name platform-{env}`

### 1. ALB Controller Pipeline (Jenkinsfile-alb-controller)
**Purpose:** Install AWS Load Balancer Controller  
**Agent:** Kubernetes pod with kubectl + AWS CLI  
**When to run:** Once per environment  
**What it does:**
- Queries VPC ID dynamically using AWS CLI
- Installs ALB controller via Helm
- Enables automatic ALB provisioning for Ingress resources

### 2. Monitoring Stack Pipeline (Jenkinsfile-monitoring)
**Purpose:** Deploy monitoring infrastructure  
**Agent:** Kubernetes pod with kubectl  
**When to run:** Once per environment  
**What it does:**
- Deploys Metrics Server (for HPA)
- Deploys Prometheus + Grafana via Helm
- Configures Grafana ingress with ALB

### 3. Application Pipeline (Jenkinsfile)
**Purpose:** Build and deploy chatbot application  
**Agent:** Kubernetes pod with Docker + kubectl  
**When to run:** Automatically on Git commits  
**What it does:**
- Builds backend/frontend Docker images
- Pushes to ECR with build number tags
- Deploys via Helm with environment-specific values
- Verifies deployment health

## Environment Management

**Global Variable:** `TARGET_ENVIRONMENT` (dev/prod) set in Jenkins  
**All pipelines:** Use Kubernetes agents (run as pods on EKS)  
**Single source of truth:** Environment configuration in Jenkins global properties

## Deployment Workflow

### Initial Setup (One-Time)
1. Set `TARGET_ENVIRONMENT` = `dev` in Jenkins global properties
2. Run **Setup Pipeline** → configures kubectl for dev cluster
3. Run **ALB Controller Pipeline** → installs ALB controller
4. Run **Monitoring Stack Pipeline** → deploys monitoring
5. Run **Application Pipeline** → deploys chatbot

### Switching Environments
1. Change `TARGET_ENVIRONMENT` to `prod` in Jenkins
2. Run **Setup Pipeline** → reconfigures kubectl for prod cluster
3. Run **ALB Controller Pipeline** → installs ALB controller in prod
4. Run **Monitoring Stack Pipeline** → deploys monitoring in prod
5. Run **Application Pipeline** → deploys chatbot to prod

### Daily Operations
- Application pipeline runs automatically on Git commits
- Uses current `TARGET_ENVIRONMENT` value
- No manual intervention needed

## Key Features

- **Kubernetes Agents:** All pipelines (except setup) run as EKS pods
- **Dynamic Configuration:** VPC ID queried at runtime, not hardcoded
- **Environment Isolation:** Single variable controls all deployments
- **Zero Downtime:** Rolling updates with health checks
- **Automated Tagging:** Build numbers used for image versioning
