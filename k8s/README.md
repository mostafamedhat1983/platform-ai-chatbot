# Kubernetes Helm Chart

Helm chart for deploying chatbot application to EKS with multi-environment support.

## Chart Structure

```
k8s/
├── Chart.yaml                    # Helm chart metadata
├── values.yaml                   # Default values (base configuration)
├── values-dev.yaml               # Development overrides
├── values-prod.yaml              # Production overrides
├── grafana-ingress.yaml          # Grafana ALB ingress (standalone)
└── templates/
    ├── chatbot-backend-deployment.yaml       # Backend pods
    ├── chatbot-backend-service.yaml          # Backend K8s service
    ├── chatbot-backend-service-account.yaml  # Pod Identity
    ├── chatbot-backend-rbac.yaml             # RBAC permissions
    ├── chatbot-backend-pdb.yaml              # Pod Disruption Budget
    ├── chatbot-frontend-deployment.yaml      # Frontend pods
    ├── chatbot-frontend-service.yaml         # Frontend K8s service
    └── chatbot-ingress.yaml                  # Chatbot ALB ingress
```

## Deployment

### Manual Deployment
```bash
# Development
helm upgrade --install chatbot . \
  -f values-dev.yaml \
  --set backend.image=<ecr-url>:backend-v1 \
  --set frontend.image=<ecr-url>:frontend-v1 \
  --namespace default

# Production
helm upgrade --install chatbot . \
  -f values-prod.yaml \
  --set backend.image=<ecr-url>:backend-v1 \
  --set frontend.image=<ecr-url>:frontend-v1 \
  --namespace default
```

### Jenkins Pipeline Deployment
Jenkins automatically overrides image tags with build numbers:
```bash
--set backend.image=${ECR_REGISTRY}/${ECR_REPOSITORY}:${BUILD_NUMBER}-backend
--set frontend.image=${ECR_REGISTRY}/${ECR_REPOSITORY}:${BUILD_NUMBER}-frontend
```

## Configuration

### Environment-Specific Values

**Development (values-dev.yaml):**
- 2 replicas per service
- 128Mi-256Mi memory, 100m-200m CPU
- HPA: 2-5 replicas (75% CPU target)
- PDB: Minimum 1 pod available

**Production (values-prod.yaml):**
- 3 replicas per service
- 256Mi-512Mi memory, 200m-500m CPU
- HPA: 3-7 replicas (70% CPU target)
- PDB: Minimum 2 pods available
- Pod anti-affinity for node distribution

### Key Features

**Security:**
- Pod Identity for AWS service authentication
- Init containers for Secrets Manager retrieval
- Non-root containers (UID 1000)
- All Linux capabilities dropped
- RBAC with least privilege

**Reliability:**
- Liveness probes (restart unhealthy pods after 30s)
- Readiness probes (traffic routing control after 5s)
- Rolling updates (MaxUnavailable=1, MaxSurge=1)
- Pod Disruption Budgets (maintain minimum availability)
- Horizontal Pod Autoscaling (CPU-based)

**Networking:**
- ALB Ingress with SSL/TLS (ACM certificate)
- Internal ClusterIP services
- Health check endpoints

## Verification

```bash
# Check deployment status
kubectl get pods -l app=chatbot-backend
kubectl get pods -l app=chatbot-frontend

# View logs
kubectl logs -l app=chatbot-backend -c chatbot-backend
kubectl logs -l app=chatbot-backend -c fetch-secrets  # Init container

# Check ingress
kubectl get ingress chatbot-ingress

# Test health
kubectl exec -it <backend-pod> -- curl localhost:8000/health
```

## Uninstall

```bash
helm uninstall chatbot -n default
```

## Notes

- Image tags in values files are placeholders (overridden by Jenkins)
- Grafana ingress deployed separately by monitoring pipeline
- Backend requires RDS credentials in Secrets Manager
- Frontend connects to backend via internal service
