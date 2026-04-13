---
layout: post
title: "Kubernetes Deployment"
description: "Deploy to Kubernetes with Deployments, Services, Ingress, HPA, and Vector sidecar pattern"
categories: [python-production]
series: python-production
module: 10
module_order: 1003
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-kubernetes-deploy
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Kubernetes is the production standard for container orchestration. It provides rolling updates, horizontal scaling, self-healing, service discovery, and secrets management. But a production-grade deployment requires multiple manifests working together.

## Namespace Isolation

```yaml
# deploy/kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: python-app
  labels:
    app: python-production-blueprint
```

Namespaces isolate your app from other workloads — separate RBAC, resource quotas, and network policies.

## ConfigMap

```yaml
# deploy/kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: python-production-blueprint-config
  namespace: python-app
data:
  APP_NAME: python-production-blueprint
  APP_ENV: production
  APP_VERSION: "0.2.0"
  APP_PORT: "8000"
  APP_WORKERS: "2"
  LOG_FORMAT: json
  LOG_LEVEL: INFO
  LOG_FILE_ENABLED: "true"
  LOG_FILE_PATH: /var/log/app/app.log
  OTEL_ENABLED: "true"
  OTEL_EXPORTER_OTLP_ENDPOINT: http://jaeger-collector.observability:4317
  OTEL_SERVICE_NAME: python-production-blueprint
  VAULT_ENABLED: "true"
  VAULT_URL: http://vault.vault:8200
  VAULT_AUTH_METHOD: approle
  VAULT_MOUNT_POINT: secret
  VAULT_SECRET_PATH: python-production-blueprint
```

## Secrets

```yaml
# deploy/kubernetes/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: vault-credentials
  namespace: python-app
type: Opaque
data:
  role-id: <base64-encoded-role-id>
  secret-id: <base64-encoded-secret-id>
```

In production, use **External Secrets Operator** or **Vault Agent Injector** instead of plain Kubernetes secrets.

## Deployment with Vector Sidecar

```yaml
# deploy/kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-production-blueprint
  namespace: python-app
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  template:
    metadata:
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      terminationGracePeriodSeconds: 30

      containers:
        # ─── Application Container ───────────────────
        - name: app
          image: your-registry/python-production-blueprint:0.2.0
          ports:
            - name: http
              containerPort: 8000
          envFrom:
            - configMapRef:
                name: python-production-blueprint-config
          env:
            - name: VAULT_ROLE_ID
              valueFrom:
                secretKeyRef:
                  name: vault-credentials
                  key: role-id
            - name: VAULT_SECRET_ID
              valueFrom:
                secretKeyRef:
                  name: vault-credentials
                  key: secret-id
          volumeMounts:
            - name: app-logs
              mountPath: /var/log/app
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 15
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 3
          startupProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 10
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            readOnlyRootFilesystem: true
            allowPrivilegeEscalation: false

        # ─── Vector Sidecar (log collector) ──────────
        - name: vector-sidecar
          image: timberio/vector:0.43.1-debian
          args: ["--config", "/etc/vector/vector.toml"]
          volumeMounts:
            - name: app-logs
              mountPath: /var/log/app
              readOnly: true
            - name: vector-config
              mountPath: /etc/vector
              readOnly: true
            - name: vector-data
              mountPath: /var/lib/vector
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 128Mi
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            readOnlyRootFilesystem: true
            allowPrivilegeEscalation: false

      volumes:
        - name: app-logs
          emptyDir:
            sizeLimit: 200Mi
        - name: vector-config
          configMap:
            name: vector-sidecar-config
        - name: vector-data
          emptyDir:
            sizeLimit: 300Mi
```

Key patterns:
- **Three probes**: startup (initial boot), liveness (keep alive), readiness (accept traffic)
- **Sidecar pattern**: Vector runs alongside the app, sharing an `emptyDir` volume for logs
- **Security context**: Non-root, read-only filesystem, no privilege escalation
- **`maxUnavailable: 0`**: Zero-downtime rolling updates

## Service

```yaml
# deploy/kubernetes/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: python-production-blueprint
  namespace: python-app
spec:
  selector:
    app: python-production-blueprint
  ports:
    - name: http
      port: 80
      targetPort: http
  type: ClusterIP
```

## Ingress

```yaml
# deploy/kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: python-production-blueprint
  namespace: python-app
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: python-production-blueprint
                port:
                  name: http
```

## Horizontal Pod Autoscaler

```yaml
# deploy/kubernetes/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: python-production-blueprint
  namespace: python-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: python-production-blueprint
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

Scales from 2 to 10 replicas based on CPU (70%) and memory (80%) utilization.

## Deployment Commands

```bash
# Apply all manifests
kubectl apply -f deploy/kubernetes/

# Watch rollout
kubectl rollout status deployment/python-production-blueprint -n python-app

# Check pods
kubectl get pods -n python-app

# View logs
kubectl logs -l app=python-production-blueprint -n python-app -c app

# Port-forward for testing
kubectl port-forward svc/python-production-blueprint 8000:80 -n python-app
```

## Next Step

In the next lesson, we explore Vector deployment patterns across platforms — sidecar vs agent vs aggregator, and when to use each.
