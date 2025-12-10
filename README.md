# AI Chatbot Platform with AWS Bedrock

![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)

Production-grade AI chatbot application deployed on **AWS EKS** with **AWS Bedrock DeepSeek V3.1**, persisting conversations to **RDS MySQL**. Features **zero-downtime deployments**, comprehensive health monitoring, and enterprise security with **Pod Identity**, **end-to-end encryption**, and **zero credential exposure** through defense-in-depth secrets management.

## 📦 Repository Scope

This repository contains the **application code and Kubernetes manifests** for the AI chatbot platform. Infrastructure provisioning (VPC, EKS, RDS, networking) lives in the separate infrastructure repository, following platform engineering best practices.

## 🎯 Project Overview

Full-stack AI chatbot demonstrating modern cloud-native architecture, serverless AI integration, and production-ready Kubernetes deployment patterns. Built from scratch with focus on security, reliability, and operational excellence.

## 🏗️ Architecture

**Two-tier application:**
- **Backend:** FastAPI REST API + AWS Bedrock DeepSeek V3.1 + MySQL conversation storage
- **Frontend:** Streamlit web interface with session management and error handling

**Deployment Stack:**
- **Container Orchestration:** Kubernetes (EKS) with Helm charts
- **AI Service:** AWS Bedrock DeepSeek V3.1 (serverless, pay-per-use)
- **Database:** RDS MySQL with Multi-AZ (prod)
- **Security:** Pod Identity for AWS authentication, init containers for secrets, RBAC, network policies, Falco runtime security
- **Monitoring:** Prometheus, Grafana, Falco (security events)
- **Reliability:** Pod Disruption Budgets, rolling updates, health checks, auto-restart

## 🛠️ What Makes This Different

**Built from scratch, not copied** - Every component researched, implemented, and debugged through hands-on learning.

**Modern AWS & Kubernetes Practices:**
- **AWS Bedrock DeepSeek V3.1** - Serverless AI with 0.27$/1M tokens (no model hosting or GPU management)
- **Pod Identity (2023)** - Direct AWS service authentication eliminating OIDC/IRSA complexity
- **Init Container Secrets** - DB credentials fetched at pod startup for improved debugging visibility
- **Multi-Environment Helm Deployment** - Single chart deploys dev/prod using values-dev.yaml and values-prod.yaml
- **Security Context** - Non-root containers (UID 1000) with privilege escalation disabled
- **Network Policies** - Zero-trust pod communication (default deny, explicit allow)
- **Vulnerability Scanning** - Trivy scans in CI/CD pipeline (fails on CRITICAL, reports HIGH/MEDIUM/LOW)
- **Health Probes** - Liveness (restart unhealthy pods after 30s) and readiness (traffic routing control after 5s)
- **Rolling Updates** - Zero-downtime deployments (MaxUnavailable=1, MaxSurge=1)
- **High Availability** - PodAntiAffinity spreads replicas across nodes, PodDisruptionBudget ensures minimum availability during node maintenance

**Security & Reliability:**
- **Zero Credential Exposure:** Secrets always encrypted (at rest in Secrets Manager with KMS, in transit via TLS 1.2+, in use loaded to memory only), never in code, images, manifests, or disk
- **End-to-End Encryption:** SSL/TLS for RDS connections, HTTPS for AWS API calls, encrypted EBS volumes
- **Pod Identity:** AWS authentication without static credentials, tokens, or OIDC configuration files
- **Pod Security Standards:** Baseline enforcement with Restricted audit/warn (Kubernetes built-in security policies)
- **Network Policies:** Zero-trust networking (default deny all, backend accepts only frontend traffic, frontend sends only to backend)
- **Vulnerability Scanning:** Automated Trivy scans in CI/CD (blocks CRITICAL vulnerabilities, archives reports)
- **Least Privilege IAM:** Backend restricted to `bedrock:InvokeModel` on specific model ARN only
- **Linux Capabilities:** All capabilities dropped (capabilities.drop: ALL) for defense against container breakout
- **Security Context:** Non-root containers (UID 1000) with seccomp profile and privilege escalation disabled
- **Resource Isolation:** Memory/CPU requests and limits prevent resource exhaustion and noisy neighbor attacks

**Code Quality:**
- FastAPI with Pydantic validation and comprehensive error handling
- Async MySQL connection pooling with proper lifecycle management
- Structured logging and health monitoring endpoints
- Containerized with optimized Docker images

## 🛠️ Technologies & Skills

**Core Stack:** Python • FastAPI • Streamlit • Docker • Kubernetes • Helm • AWS Bedrock • RDS MySQL • AWS Secrets Manager

**Key Capabilities:**
- **Cloud-Native Development:** Containerized microservices, Kubernetes deployments, Helm charts, Pod Identity
- **AI Integration:** AWS Bedrock API integration, prompt engineering, conversation context management
- **Backend Engineering:** FastAPI async APIs, Pydantic validation, MySQL connection pooling, error handling
- **Security:** Init container secrets, Pod Identity, RBAC, zero credential exposure
- **Reliability:** Health checks, rolling updates, PDBs, graceful shutdown, automatic restart, session persistence

## 📁 Project Structure

```
platform-ai-chatbot/
├── backend/
│   ├── main.py              # FastAPI app with Bedrock & MySQL integration
│   ├── Dockerfile           # Backend container image
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── app.py               # Streamlit UI with session management
│   ├── Dockerfile           # Frontend container image
│   └── requirements.txt     # Python dependencies
├── jenkins/
│   ├── Jenkinsfile                  # Application CI/CD pipeline
│   ├── Jenkinsfile-setup            # kubectl context configuration
│   ├── Jenkinsfile-alb-controller   # ALB controller deployment
│   └── Jenkinsfile-monitoring       # Monitoring stack deployment
└── k8s/
    ├── Chart.yaml           # Helm chart metadata
    ├── values.yaml          # Default Helm values
    ├── values-dev.yaml      # Development overrides
    ├── values-prod.yaml     # Production overrides
    ├── grafana-ingress.yaml # Grafana ALB ingress (used by monitoring pipeline)
    └── templates/
        ├── namespace.yaml                       # Namespace with Pod Security Standards
        ├── chatbot-backend-deployment.yaml      # Backend pods
        ├── chatbot-backend-service.yaml         # Backend K8s service
        ├── chatbot-backend-service-account.yaml # Pod Identity
        ├── chatbot-backend-rbac.yaml            # RBAC permissions
        ├── chatbot-backend-pdb.yaml             # Disruption budget
        ├── chatbot-backend-hpa.yaml             # Horizontal Pod Autoscaler
        ├── chatbot-frontend-deployment.yaml     # Frontend pods
        ├── chatbot-frontend-service.yaml        # Frontend K8s service
        ├── chatbot-frontend-pdb.yaml            # Frontend disruption budget
        ├── ingress.yaml                         # Chatbot ALB ingress
        ├── network-policy-default-deny.yaml     # Default deny all traffic
        ├── network-policy-backend.yaml          # Backend network rules
        ├── network-policy-frontend.yaml         # Frontend network rules
        └── storage-class.yaml                   # EBS storage class
```

## 🔒 Security Architecture

**Defense-in-Depth: Secrets Always Encrypted, Never Exposed**

Every layer designed to ensure credentials are **always safe** through comprehensive encryption and zero persistence:

### Secrets Management Lifecycle

**1. Encrypted at Rest (AWS Secrets Manager):**
- RDS credentials stored in AWS Secrets Manager
- Encrypted with AWS KMS customer-managed keys
- Access controlled via IAM policies (Pod Identity)
- Supports automatic rotation without application changes

**2. Encrypted in Transit (TLS 1.2+):**
- Init container fetches secrets via AWS API over HTTPS
- All AWS service calls (Bedrock, Secrets Manager) encrypted in transit

**3. Encrypted in Use (Memory-Only):**
- Secrets loaded directly into application memory at pod startup
- **Never written to disk:** No ConfigMaps, environment variables, or log files
- **Never in images:** Zero credentials baked into container images
- **Never in manifests:** Helm charts reference secret names only, not values
- Process memory cleared on pod termination

**Why Init Containers over CSI Driver:**
Evaluated AWS Secrets Store CSI Driver but chose init containers for:
- ✅ **Better debugging:** Logs visible in application pod (`kubectl logs <pod> -c fetch-secrets`)
- ✅ **Simpler architecture:** No CSI addon, SecretProviderClass, or volume mounts
- ✅ **Direct error visibility:** AWS API errors shown immediately in init container logs
- ✅ **Full control:** Complete visibility into secret retrieval logic
- ⚠️ **Trade-off:** Manual pod restart for secret rotation (acceptable for infrequent DB credential changes)

### AWS Authentication (Pod Identity)

- **No Static Credentials:** Pods assume IAM role via EKS Pod Identity (eliminates access keys, OIDC tokens, service account token files)
- **Temporary Credentials:** AWS SDK automatically retrieves and refreshes short-lived tokens
- **Least Privilege:** IAM policy allows only `bedrock:InvokeModel` on specific DeepSeek V3.1 model ARN
- **Audit Trail:** All AWS API calls logged in CloudTrail with pod identity context

### Database Security

- **Encrypted Storage:** RDS volumes encrypted with KMS (managed in infrastructure repository)
- **Network Isolation:** RDS in private subnets, no public internet access
- **Connection Pooling:** Credentials reused across pooled connections without re-fetch

### Kubernetes Security

- **Pod Security Standards:** Baseline enforcement with Restricted audit/warn (blocks privilege escalation, enforces seccomp profiles)
- **RBAC:** Service account permissions limited to required Kubernetes resources only
- **Network Policies:** Zero-trust networking with default deny all, backend accepts ingress only from frontend, frontend egress only to backend + DNS

## 💡 Key Technical Decisions

Architecture choices made through research and hands-on evaluation:

- **AWS Bedrock DeepSeek V3.1:** Serverless AI (no GPU management), pay-per-use ($0.27/1M tokens), 64K context window for conversation history
- **Init Container Secrets:** Chosen over AWS Secrets Store CSI Driver for better debugging visibility (logs in app pod), simpler architecture (no CSI addon), and direct AWS API error messages
- **FastAPI Async:** Non-blocking I/O for AI and database calls, connection pooling, lifespan management
- **Multi-Environment Helm:** Single chart with environment-specific values files eliminates manifest duplication, supports GitOps workflows
- **Session Persistence:** MySQL storage enables conversation continuity across pod restarts

## 🚀 Complete Deployment Guide

### Prerequisites
- EKS cluster with Pod Identity (see terraform-aws-eks repository)
- RDS MySQL with Secrets Manager credentials
- AWS Bedrock DeepSeek V3.1 access in us-east-2
- ECR repository: `platform-app`
- Jenkins with Kubernetes plugin configured
- Domain with DNS access (e.g., Namecheap)

### Phase 1: SSL Certificate Setup

**With Custom Domain:**

**1. Request Certificate:**
```bash
aws acm request-certificate \
  --domain-name "*.your-domain.com" \
  --validation-method DNS \
  --region us-east-2
# Note the CertificateArn
```

**2. Add Validation CNAME:**
- Get validation record: `aws acm describe-certificate --certificate-arn <arn>`
- Add CNAME to domain DNS (e.g., Namecheap)
- Wait for status: ISSUED (~5-30 min)

**3. Update Ingress Annotations:**
Update certificate ARN in `k8s/values-dev.yaml` and `k8s/values-prod.yaml`:
```yaml
chatbot:
  ingress:
    certificateArn: arn:aws:acm:us-east-2:xxx:certificate/xxx
```

**Without Custom Domain:** See [Deployment Without Custom Domain](#deployment-without-custom-domain) below

### Phase 2: Jenkins Pipeline Setup

**1. Configure Jenkins-Kubernetes Integration:**
```bash
# Connect to Jenkins EC2 via SSM
aws ssm start-session --target <jenkins-instance-id> --region us-east-2

# Create service account and token
aws eks update-kubeconfig --name platform-dev --region us-east-2
kubectl create serviceaccount jenkins-sa -n default
kubectl create clusterrolebinding jenkins-admin --clusterrole=cluster-admin --serviceaccount=default:jenkins-sa
kubectl create token jenkins-sa --duration=8760h -n default  # Copy token
```

**Add to Jenkins:**
- Credentials → Add → Kind: Secret text, ID: `jenkins-k8s-token`, paste token
- Configure Clouds → Add Kubernetes → URL: `https://<eks-endpoint>`, Namespace: default, Credentials: jenkins-k8s-token
- ☑️ Disable https certificate check | ☑️ WebSocket

**2. Configure Environment Variable:**
- Manage Jenkins → System → Global properties
- Add: `TARGET_ENVIRONMENT` = `dev` (or `prod`)

**3. Run Pipelines in Order:**

**1. Setup Pipeline** (Jenkinsfile-setup)
```
Purpose: Configure kubectl on Jenkins EC2
Runs on: Jenkins EC2 (agent any)
Frequency: Once per environment
```

**2. ALB Controller Pipeline** (Jenkinsfile-alb-controller)
```
Purpose: Install AWS Load Balancer Controller
Runs on: Kubernetes pod
Frequency: Once per environment
Creates: ALB controller (no ALBs yet)
```

**3. Monitoring Pipeline** (Jenkinsfile-monitoring)
```
Purpose: Deploy Metrics Server + Prometheus + Grafana
Runs on: Kubernetes pod
Frequency: Once per environment
Creates: Grafana ingress → triggers first ALB creation
```

**4. Application Pipeline** (Jenkinsfile)
```
Purpose: Build images + deploy chatbot
Runs on: Kubernetes pod
Frequency: Automatic on Git commits
Creates: Chatbot ingress → uses shared ALB (dev) or separate ALB (prod)
```

**Why 4 Pipelines?**
- **Separation of concerns:** Infrastructure setup vs application deployment
- **Different lifecycles:** Setup/ALB/monitoring run once, application runs continuously
- **Different agents:** Setup needs Jenkins EC2 for kubectl config, others use ephemeral Kubernetes pods
- **Easier troubleshooting:** Each pipeline has single responsibility

### Phase 3: DNS Configuration

**1. Get ALB DNS Names:**
```bash
kubectl get ingress --all-namespaces
```

**2. Add CNAME Records:**

**Dev (1 shared ALB):**
| Host    | Type  | Value                                    |
|---------|-------|------------------------------------------|
| chatbot | CNAME | k8s-platformsharedalb-xxx.elb.amazonaws.com |
| grafana | CNAME | k8s-platformsharedalb-xxx.elb.amazonaws.com |

**Prod (2 separate ALBs):**
| Host    | Type  | Value                                |
|---------|-------|--------------------------------------|
| chatbot | CNAME | k8s-chatbot-xxx.elb.amazonaws.com    |
| grafana | CNAME | k8s-grafana-xxx.elb.amazonaws.com    |

**Why Different ALB Strategies?**
- **Dev:** 1 shared ALB saves cost (~$16/month), acceptable for non-production
- **Prod:** 2 separate ALBs provide isolation, independent scaling (~$32/month)

### Phase 4: Verification

```bash
# Check DNS resolution
nslookup chatbot.your-domain.com

# Test HTTPS access
curl -I https://chatbot.your-domain.com
curl -I https://grafana.your-domain.com

# Check pods
kubectl get pods -l app=chatbot-backend
kubectl get pods -l app=chatbot-frontend

# View logs
kubectl logs -l app=chatbot-backend -c chatbot-backend
kubectl logs -l app=chatbot-backend -c fetch-secrets  # Init container
```

### Deployment Timing
- SSL certificate validation: 5-30 min
- Setup pipeline: 1 min
- ALB controller pipeline: 3-5 min
- Monitoring pipeline: 5-10 min
- Application pipeline: 5-8 min
- DNS propagation: 5-10 min
- **Total first deployment:** ~30-60 min
- **Subsequent deployments:** ~5-8 min (application pipeline only)

### Monitoring Access

**Grafana (via ALB or port-forward):**
```bash
# Option 1: ALB (if DNS configured)
https://grafana.your-domain.com
# Credentials: admin / admin

# Option 2: Port-forward (no ALB needed)
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Open http://localhost:3000
# Credentials: admin / admin
```

**Falco Security Events (port-forward only):**
```bash
# Falcosidekick UI
kubectl port-forward -n falco svc/falco-falcosidekick-ui 2802:2802
# Open http://localhost:2802

# View Falco in Grafana
# Import dashboard ID: 11914 (Prometheus auto-scrapes Falco metrics)
```

**Prometheus (port-forward only):**
```bash
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# Open http://localhost:9090
```



## Deployment Without Custom Domain

### Option 1: HTTP Only
⚠️ No encryption - for testing only

1. Skip Phase 1, update `k8s/values-dev.yaml`:
   ```yaml
   chatbot:
     ingress:
       annotations:
         alb.ingress.kubernetes.io/listen-ports: '[{"HTTP":80}]'
   ```
2. Deploy (Phase 2-4), access via: `http://k8s-chatbot-xxx.elb.amazonaws.com`

### Option 2: Self-Signed Certificate
⚠️ Browser warnings - for HTTPS testing

1. Generate and upload:
   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=*.elb.amazonaws.com"
   aws acm import-certificate --certificate fileb://tls.crt --private-key fileb://tls.key --region us-east-2
   ```
2. Update `k8s/values-dev.yaml` with certificateArn, deploy (Phase 2-4)
3. Access: `https://k8s-chatbot-xxx.elb.amazonaws.com` (accept warning)

**Production:** Use free domains (DuckDNS, Freenom) + Let's Encrypt via cert-manager.

## 🔄 CI/CD Integration

**Jenkins Pipeline:**

Automated deployment via Jenkins with 4 pipelines:

**0. Setup Pipeline (Jenkinsfile-setup):**
- Configures kubectl context on Jenkins EC2
- Run once per environment or when switching between dev/prod
- Enables Kubernetes agent pods for all other pipelines

**1. ALB Controller Pipeline (Jenkinsfile-alb-controller):**
- Deploys AWS Load Balancer Controller to EKS
- Enables automatic ALB provisioning for Ingress resources
- Run once per environment

**2. Monitoring Stack Pipeline (Jenkinsfile-monitoring):**
- Deploys Metrics Server (for HPA), Prometheus, Grafana, and Falco
- Configures Grafana ingress with ALB (optional)
- Falco provides runtime security monitoring with Falcosidekick UI
- Run once per environment

**3. Application Pipeline (Jenkinsfile):**
- Builds Docker images with versioned tags
- Pushes to ECR with automated authentication
- Scans images with Trivy (fails on CRITICAL vulnerabilities, reports HIGH/MEDIUM/LOW)
- Deploys with Helm using environment-specific values
- Verifies deployment health
- Triggered automatically on Git commits
- Scan reports archived in Jenkins (Build → Artifacts → *-scan.json)

**Environment Management:**
- Global `TARGET_ENVIRONMENT` variable (dev/prod) set in Jenkins
- All pipelines use Kubernetes agents (run as pods on EKS)
- Single source of truth for environment configuration

**GitOps Alternative:**
Helm charts support ArgoCD/FluxCD for declarative deployments with automatic sync from Git.

## 📊 Resource Configuration

**Development Environment:**
- Backend: 2 replicas, 128Mi-256Mi memory, 100m-200m CPU
- Frontend: 2 replicas, 128Mi-256Mi memory, 100m-200m CPU
- HPA: 2-5 replicas based on CPU (75% target)
- Total: ~1GB memory, ~800m CPU per environment

**Production Environment:**
- Backend: 3 replicas, 256Mi-512Mi memory, 200m-500m CPU
- Frontend: 3 replicas, 256Mi-512Mi memory, 200m-500m CPU
- HPA: 3-7 replicas based on CPU (70% target)
- Pod Disruption Budget: Minimum 2 pods available during disruptions
- Anti-affinity: Prefer different nodes for replica distribution

## 🔮 Future Enhancements

**GitOps with ArgoCD:**
Implement ArgoCD for declarative GitOps deployments with automatic sync from Git, providing audit trail, easy rollbacks, and separation between build (Jenkins) and deploy (ArgoCD) phases.

**External Secrets Operator:**
Replace init containers with External Secrets Operator for automatic secret rotation and centralized secret management across multiple secrets sources (Secrets Manager, Parameter Store, Vault).

**Additional Planned Enhancements:**
- Prometheus metrics export for observability
- Rate limiting and request throttling
- Multi-region deployment for disaster recovery
- A/B testing infrastructure for model comparison
- Automated testing (pytest for backend, integration tests)
- API documentation with FastAPI /docs screenshots

## 🤖 AI-Assisted Development

Frontend and backend application code generated with **Claude Sonnet 4.5** to accelerate development and focus efforts on DevOps implementation. Kubernetes manifests, Helm charts, deployment architecture, and infrastructure integration were human-designed and built from scratch. This approach demonstrates modern AI-augmented workflows where AI handles repetitive application scaffolding while engineers focus on architecture, security, and operational excellence.

## 🎓 Key Learnings

1. Init containers provide better debugging visibility than CSI driver approaches (logs in application pod vs kube-system namespace)
2. Pod Identity eliminates OIDC/IRSA complexity while providing same AWS service authentication
3. Multi-environment Helm deployment with values files eliminates manifest duplication and reduces configuration drift
4. Pod Disruption Budgets + health probes + rolling updates critical for zero-downtime deployments during cluster maintenance
5. Async MySQL connection pooling essential for scalable database access under concurrent AI request load
6. Secrets encrypted at rest (KMS), in transit (TLS 1.2+), and in use (memory-only) ensures zero credential exposure
7. Non-root containers with resource limits prevent privilege escalation and resource exhaustion attacks
8. Dropping all Linux capabilities provides defense-in-depth against container breakout exploits
9. Network policies implement zero-trust (default deny, explicit allow) without infrastructure changes - pure Kubernetes resources
10. Trivy vulnerability scanning in CI/CD catches security issues before production deployment
11. Falco runtime security monitoring detects suspicious behavior (shell spawns, file changes, privilege escalation) with Grafana integration
12. Pod Security Standards enforce Kubernetes security policies (baseline enforcement prevents privilege escalation, seccomp profiles restrict syscalls)

## 🤝 Contributing

Personal learning project, but feedback welcome! Open issues or reach out.

## 📄 License

MIT License

---

**Built with:** Python, FastAPI, Streamlit, Kubernetes, AWS Bedrock, and hands-on iteration 🚀

**Note:** Every line written with understanding, not copied from templates. Each decision tested, every issue debugged, every improvement learned through practice.
