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
- **Database:** RDS MySQL with SSL/TLS encryption and Multi-AZ (prod)
- **Security:** Pod Identity for AWS authentication, init containers for secrets, RBAC
- **Reliability:** Pod Disruption Budgets, rolling updates, health checks, auto-restart

## 🛠️ What Makes This Different

**Built from scratch, not copied** - Every component researched, implemented, and debugged through hands-on learning.

**Modern AWS & Kubernetes Practices:**
- **AWS Bedrock DeepSeek V3.1** - Serverless AI with 0.27$/1M tokens (no model hosting or GPU management)
- **Pod Identity (2023)** - Direct AWS service authentication eliminating OIDC/IRSA complexity
- **Init Container Secrets** - DB credentials fetched at pod startup for improved debugging visibility
- **Multi-Environment Helm Deployment** - Single chart deploys dev/prod using values-dev.yaml and values-prod.yaml
- **Security Context** - Non-root containers (UID 1000) with privilege escalation disabled
- **Health Probes** - Liveness (restart unhealthy pods after 30s) and readiness (traffic routing control after 5s)
- **Rolling Updates** - Zero-downtime deployments (MaxUnavailable=1, MaxSurge=1)
- **High Availability** - PodAntiAffinity spreads replicas across nodes, PodDisruptionBudget ensures minimum availability during node maintenance

**Security & Reliability:**
- **Zero Credential Exposure:** Secrets always encrypted (at rest in Secrets Manager with KMS, in transit via TLS 1.2+, in use loaded to memory only), never in code, images, manifests, or disk
- **End-to-End Encryption:** SSL/TLS for RDS connections, HTTPS for AWS API calls, encrypted EBS volumes
- **Pod Identity:** AWS authentication without static credentials, tokens, or OIDC configuration files
- **Least Privilege IAM:** Backend restricted to `bedrock:InvokeModel` on specific model ARN only
- **Security Context:** Non-root containers (UID 1000) with privilege escalation disabled
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
- **Security:** SSL/TLS encryption, init container secrets, Pod Identity, RBAC, zero credential exposure
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
└── k8s/
    ├── Chart.yaml           # Helm chart metadata
    ├── values.yaml          # Default Helm values
    ├── values-dev.yaml      # Development overrides
    ├── values-prod.yaml     # Production overrides
    └── templates/
        ├── chatbot-backend-deployment.yaml      # Backend pods
        ├── chatbot-backend-service.yaml         # Backend K8s service
        ├── chatbot-backend-service-account.yaml # Pod Identity
        ├── chatbot-backend-rbac.yaml            # RBAC permissions
        └── chatbot-backend-pdb.yaml             # Disruption budget
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
- MySQL connections use SSL/TLS encryption end-to-end
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

- **SSL/TLS Connections:** All MySQL traffic encrypted end-to-end (backend → RDS)
- **Encrypted Storage:** RDS volumes encrypted with KMS (managed in infrastructure repository)
- **Network Isolation:** RDS in private subnets, no public internet access
- **Connection Pooling:** Credentials reused across pooled connections without re-fetch

### Kubernetes Security

- **RBAC:** Service account permissions limited to required Kubernetes resources only
- **Network Policies:** (Planned) Restrict pod-to-pod traffic to required services only

## 💡 Key Technical Decisions

Architecture choices made through research and hands-on evaluation:

- **AWS Bedrock DeepSeek V3.1:** Serverless AI (no GPU management), pay-per-use ($0.27/1M tokens), 64K context window for conversation history
- **Init Container Secrets:** Chosen over AWS Secrets Store CSI Driver for better debugging visibility (logs in app pod), simpler architecture (no CSI addon), and direct AWS API error messages
- **FastAPI Async:** Non-blocking I/O for AI and database calls, connection pooling, lifespan management
- **Multi-Environment Helm:** Single chart with environment-specific values files eliminates manifest duplication, supports GitOps workflows
- **Session Persistence:** MySQL storage enables conversation continuity across pod restarts

## 🚀 Deployment

**Prerequisites:**
- EKS cluster with Pod Identity enabled (see infrastructure repository)
- RDS MySQL instance with SSL/TLS (see infrastructure repository)
- AWS Bedrock model access (DeepSeek V3.1 in us-east-2)
- ECR repository for container images
- Secrets Manager with RDS credentials (created during infrastructure setup)
- kubectl configured for EKS cluster access
- Helm 3.x installed

**1. Build and Push Container Images:**

```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-2 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-2.amazonaws.com

# Build and push backend
cd backend
docker build -t <account-id>.dkr.ecr.us-east-2.amazonaws.com/platform-app:backend-v1.0.0 .
docker push <account-id>.dkr.ecr.us-east-2.amazonaws.com/platform-app:backend-v1.0.0

# Build and push frontend
cd ../frontend
docker build -t <account-id>.dkr.ecr.us-east-2.amazonaws.com/platform-app:frontend-v1.0.0 .
docker push <account-id>.dkr.ecr.us-east-2.amazonaws.com/platform-app:frontend-v1.0.0
```

**2. Update Helm Values:**

Edit `k8s/values-dev.yaml` or `k8s/values-prod.yaml`:
```yaml
backend:
  image: <account-id>.dkr.ecr.us-east-2.amazonaws.com/platform-app:backend-v1.0.0

frontend:
  image: <account-id>.dkr.ecr.us-east-2.amazonaws.com/platform-app:frontend-v1.0.0
```

**3. Deploy with Helm:**

```bash
cd k8s

# Development
helm upgrade --install chatbot . \
  -f values-dev.yaml \
  --namespace default

# Production
helm upgrade --install chatbot . \
  -f values-prod.yaml \
  --namespace default
```

**4. Verify Deployment:**

```bash
# Check pod status
kubectl get pods -l app=chatbot-backend

# View backend logs
kubectl logs -l app=chatbot-backend -c chatbot-backend

# Check init container logs (secrets fetch)
kubectl logs -l app=chatbot-backend -c fetch-secrets

# Verify health
kubectl exec -it <backend-pod> -- curl localhost:8000/health
```

**5. Access Application:**

```bash
# Port forward to access frontend locally
kubectl port-forward service/chatbot-frontend 8501:8501

# Open browser to http://localhost:8501
```

**Timing:**
- Container builds: ~3-5 min
- ECR push: ~1-2 min
- Helm deployment: ~2-3 min
- Pod startup: ~30-60 sec (includes init container secrets fetch)

## 🔄 CI/CD Integration

**Jenkins Pipeline (Planned):**
1. Checkout code from Git
2. Build Docker images with versioned tags
3. Push to ECR with automated authentication
4. Run Helm upgrade with environment-specific values
5. Verify deployment health and rollback on failure

**GitOps Alternative:**
Helm charts support ArgoCD/FluxCD for declarative deployments with automatic sync from Git.

## 📊 Resource Configuration

**Development Environment:**
- Backend: 1 replica, 128Mi-256Mi memory, 100m-200m CPU
- Frontend: 1 replica, 128Mi-256Mi memory, 100m-200m CPU
- Total: ~512Mi memory, ~400m CPU per environment

**Production Environment:**
- Backend: 2+ replicas (HA), same resource limits
- Pod Disruption Budget: Minimum 1 pod available during disruptions
- Anti-affinity: Prefer different nodes for replica distribution

## 🔮 Future Enhancements

**External Secrets Operator:**
Replace init containers with External Secrets Operator for automatic secret rotation and centralized secret management across multiple secrets sources (Secrets Manager, Parameter Store, Vault).

**Additional Planned Enhancements:**
- Horizontal Pod Autoscaler (HPA) based on CPU/memory metrics
- Network policies for pod-to-pod communication restrictions
- Prometheus metrics export for observability
- Ingress/ALB for production-grade load balancing
- Rate limiting and request throttling
- Multi-region deployment for disaster recovery
- A/B testing infrastructure for model comparison

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

## 🤝 Contributing

Personal learning project, but feedback welcome! Open issues or reach out.

## 📄 License

MIT License

---

**Built with:** Python, FastAPI, Streamlit, Kubernetes, AWS Bedrock, and hands-on iteration 🚀

**Note:** Every line written with understanding, not copied from templates. Each decision tested, every issue debugged, every improvement learned through practice.
