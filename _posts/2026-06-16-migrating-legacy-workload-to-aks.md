---
layout: blog
title: "How We Migrated a High-Traffic Recommendation Stack to AKS Without Downtime"
description: "A field-report style walkthrough of moving an on-premise recommendation platform into Azure AKS: Application Gateway, internal NGINX ingress, persistent VMs for Cassandra/Kafka/Elasticsearch, and the ranking engine that had to stay on local disk."
categories: [Azure, AKS, Kubernetes, Migration, Architecture]
tags: [Azure, AKS, Kubernetes, Application Gateway, NGINX Ingress, Migration, Helm, Hybrid Cloud]
image: ""
---

We had a hard deadline, a platform that served millions of recommendations per day, and a data center lease that was not going to renew itself.

The system was a generic recommendation platform — content feeds, item suggestions, user profiles, search, and real-time events. It had grown over ten years into a classic enterprise stack: virtual machines for data services, a Marathon container orchestrator for stateless apps, and multiple tiers of load balancers held together with configuration files that only a few people in the company dared to edit.

This is the story of how we moved it to **Azure Kubernetes Service (AKS)**.

It is not a polished vendor case study. It is what actually happened: the replacements we chose, the service that refused to containerize, the late-night surprises, and the architecture we ended up with.

---

## What We Were Dealing With

### The On-Premise Stack

```
Internet
   │
   ▼
Frontend load balancer (active/standby pair)
   ├── /feed             → feed API
   ├── /recommend        → recommendation engine
   ├── /items            → item catalog API
   └── /users            → user profile API

Regional load balancer (per data center)
   ├── /recommend/*      → ranking engine VMs
   └── /events           → event ingestion API

Local load balancer (per host)
   └── internal services on legacy container platform
```

Behind those load balancers sat:

- **Cassandra** — primary data store, three nodes per data center
- **Kafka** — event streaming and log pipeline, three brokers
- **Elasticsearch** — search and content index, three nodes
- **Consul** — service discovery and configuration
- **Marathon** — stateless microservices
- **Ranking engine VMs** — the core recommendation runtime, running a large file-backed in-memory index on local disk

Everything was stable, but everything was also tightly coupled to the data center. We needed to move to Azure without rewriting ten years of code.

---

## The Strategy: Replatform, Not Rebuild

We decided on a hybrid migration:

1. **Keep the data layer on Azure VMs** — Cassandra, Kafka, Elasticsearch, and Consul needed predictable disk I/O and were not yet ready for Kubernetes.
2. **Move stateless microservices into AKS** — this gave us Helm-based deployments, auto-scaling, and faster release cycles.
3. **Replace public load balancers with Azure Application Gateway** — managed L7 gateway with TLS termination and path-based routing.
4. **Add an internal NGINX ingress controller** — low-latency, VNet-private routing from VMs and pods to other pods.
5. **Bridge the ranking engine VMs into Kubernetes** — so AKS services could reach them through standard Kubernetes service names.

The result was not 100% Kubernetes. It was a pragmatic hybrid that let us migrate incrementally and sleep at night.

---

## Phase 1: Landing the Data Layer on Azure VMs

The first thing we moved was the foundation: Cassandra, Kafka, and Elasticsearch.

These were not containerized. They ran on dedicated Azure VMs with large managed disks because Kubernetes persistent volumes at the scale we needed would have added complexity we were not ready for.

| Service | Azure VM Size | Disk | Role |
|---|---|---|---|
| Cassandra | Standard_E16s_v5 | 6 TB each | Primary transactional store |
| Kafka | Standard_E16s_v5 | 1.2 TB each | Event streaming / log pipeline |
| Elasticsearch | Standard_E16s_v5 | 1.2 TB each | Search and content index |
| Consul | Container on VM | — | Service discovery bridge |

We kept the same replication topology, the same JVM tuning, and the same operational runbooks. The only thing that changed was the hardware underneath. This gave the data team confidence and bought us time to think about Kubernetes later.

---

## Phase 2: Moving Stateless Services to AKS

Next came the microservices. We built a reusable Helm chart called `recommendation-apps` and used it to deploy around thirty services into AKS.

Some of the services:

- `feed-api` — public content feed API
- `item-catalog` — item metadata and inventory
- `user-profile` — profile CRUD and preferences
- `ranking-service` — scoring and ranking logic
- `search-service` — search query handling
- `event-collector` — real-time event ingestion
- `notification-service` — alerts and notifications
- `analytics-sink` — event aggregation and reporting

The Helm chart standardized:

- Rolling and recreate deployment strategies
- Liveness, readiness, and startup probes
- Horizontal pod autoscaling
- Pod disruption budgets for HA services
- ConfigMap-driven configuration with checksum-based rollouts
- Internal load balancer, ClusterIP, and headless service types

A typical deployment went from a manual, multi-step process to a single command:

```bash
helm upgrade --install ranking-service ./recommendation-apps \
  -f values-azure/values-ranking-service.yaml \
  -n recommendation-prod
```

That alone changed how the team shipped software.

---

## Phase 3: Replacing Public Load Balancers with Application Gateway

The on-premise setup used a pair of HAProxy load balancers for public traffic. We replaced them with **Azure Application Gateway** and its Kubernetes ingress controller.

Why Application Gateway?

- It could route to **both AKS pods and external VM endpoints** from a single gateway
- It handled SSL termination and offered WAF on the WAF_v2 SKU
- It had active health probes, so a failed VM backend would be removed automatically

The public routing ended up like this:

```
Internet → Azure Application Gateway
   ├── /recommend/*      → ranking engine VMs (via Service + Endpoints)
   ├── /feed/*           → feed-api pods
   ├── /items/*          → item-catalog pods
   ├── /users/*          → user-profile pods
   └── /events/*         → event-collector pods
```

Because the ranking engine was still on VMs, we represented those VMs as Kubernetes `Service` and `Endpoints` objects with static IPs. Application Gateway never knew the difference.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ranking-engine
  namespace: recommendation-prod
spec:
  ports:
    - port: 80
      targetPort: 8080
---
apiVersion: v1
kind: Endpoints
metadata:
  name: ranking-engine
  namespace: recommendation-prod
subsets:
  - addresses:
      - ip: <ranking-vm-1>
      - ip: <ranking-vm-2>
    ports:
      - port: 8080
```

The public ingress then routed `/recommend` to that service:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: recommend-external
  namespace: recommendation-prod
  annotations:
    appgw.ingress.kubernetes.io/backend-protocol: http
    appgw.ingress.kubernetes.io/health-probe-path: /health
    appgw.ingress.kubernetes.io/health-probe-port: "8080"
    appgw.ingress.kubernetes.io/connection-draining: "true"
    appgw.ingress.kubernetes.io/connection-draining-timeout: "30"
spec:
  ingressClassName: azure-application-gateway
  rules:
    - http:
        paths:
          - path: /recommend
            pathType: Prefix
            backend:
              service:
                name: ranking-engine
                port:
                  number: 80
```

---

## Phase 4: Building the Internal Nerve Center with NGINX

Inside the virtual network, the ranking VMs needed to call pod-based services like `search-service`, `ranking-service`, `user-profile`, and `event-collector`. On-premise, every VM had its own local load balancer configuration. In Azure, we replaced that with one **internal NGINX Ingress Controller** fronted by an Azure internal load balancer.

We chose this because latency mattered. The ranking engine issued thousands of internal lookups per second. Adding an L7 appliance or a NAT layer would have added milliseconds we did not have.

| Option | Latency | Verdict |
|---|---|---|
| Internal NGINX + Azure internal LB | ~0.3 ms | ✅ Same VNet, kernel-level L4 forwarding |
| Private Link / private endpoint | ~0.5–1 ms | Adds NAT overhead |
| Internal application gateway | ~1–5 ms | L7 overhead, not needed internally |
| API management | ~5–15 ms | Too heavy for service-to-service calls |

We installed NGINX with a static private IP and the internal load balancer annotation:

```yaml
controller:
  replicaCount: 3
  ingressClassResource:
    name: recommendation-internal-nginx
  service:
    annotations:
      service.beta.kubernetes.io/azure-load-balancer-internal: "true"
    loadBalancerIP: <static-private-ip>
    externalTrafficPolicy: Local
  config:
    proxy-connect-timeout: "5"
    proxy-read-timeout: "60"
    proxy-send-timeout: "60"
    ssl-redirect: "false"
```

Then every internal service got a declarative ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: search-service-internal
  namespace: recommendation-prod
  annotations:
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "5"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: recommendation-internal-nginx
  rules:
    - http:
        paths:
          - path: /search
            pathType: Prefix
            backend:
              service:
                name: search-service
                port:
                  number: 80
```

Now the ranking VMs talked to one stable private IP instead of managing a dozen backend addresses.

---

## Phase 5: The Service That Refused to Move

The most interesting part of the migration was the ranking engine.

It used a multi-gigabyte in-memory index that was snapshotted to local disk — similar to a large embedded key-value store or serialized search index. Rebuilding that index from remote storage took several minutes. Network-attached disks added latency that degraded query response times. And pod rescheduling would have meant replicating the index across nodes, which was neither fast nor cheap.

We tried to containerize it. We ran the numbers. We built a proof of concept. And then we decided to leave it on VMs.

| Concern | Why the VM won |
|---|---|
| **Disk latency** | Local NVMe gave sub-millisecond access to the index. Remote storage did not. |
| **Cold start** | A pod restart would rebuild the index for minutes. A VM restart had the disk ready. |
| **Affinity** | The data was tied to the host. Kubernetes node churn would fight that. |
| **Risk** | It was the revenue engine. Moving it before the surrounding platform was stable was not worth the gamble. |

So the ranking engine stayed on two dedicated Azure VMs, and we bridged it into Kubernetes with `Service` + `Endpoints`. Both the public Application Gateway and the internal NGINX ingress could route to it by name.

This was the defining decision of the migration: **Kubernetes does not have to own every workload.** Sometimes the right move is to give a VM a Kubernetes service contract and call it a day.

---

## Phase 6: The Cutover

We ran the old and new environments side by side for several weeks.

1. **Validate data replication** — Cassandra, Kafka, and Elasticsearch were replicating correctly between on-premise and Azure.
2. **Mirror traffic** — we sent a percentage of read traffic through Application Gateway to confirm latency and error rates.
3. **Lower DNS TTL** — 24 hours before cutover, we dropped the TTL on the public endpoints to 60 seconds.
4. **Switch DNS** — on cutover night, we flipped the A records from the old public IPs to Application Gateway.
5. **Watch and wait** — we monitored request rates, error rates, and recommendation latency for 48 hours before declaring victory.

The actual DNS switch took under a minute. The nervous part was the two days after.

---

## What Broke, and What We Learned

### Lesson 1: Health Probes Are Not Equal Everywhere

Application Gateway actively probes the ranking VMs and removes a failed node in about six seconds. The internal NGINX path, however, relies on Kubernetes `Endpoints` and kube-proxy. kube-proxy does not health-check static VM IPs — it round-robins them forever.

When one ranking VM had an issue:

- **Public path:** ~6 seconds of failed requests, then automatic recovery
- **Internal path:** ~50% of internal requests kept timing out until we manually patched the `Endpoints` object

For planned maintenance, we scripted an out-of-rotation procedure:

```bash
# Remove a VM from the ranking service
DEAD_IP="<ranking-vm-1>"
kubectl get endpoints ranking-engine -n recommendation-prod -o json \
  | jq --arg ip "$DEAD_IP" \
      '.subsets[0].addresses = [.subsets[0].addresses[] | select(.ip != $ip)]' \
  | kubectl apply -f -

# Wait for connection draining
sleep 30

# Now it is safe to restart the VM
```

For unplanned failures, we later added a service-mesh sidecar with outlier detection so pods could eject a bad VM automatically. But on day one, the runbook was enough.

### Lesson 2: Two Ingress Controllers Are Better Than One

We ran two ingress controllers in the same AKS cluster:

| Controller | Class | Traffic | IP |
|---|---|---|---|
| Application Gateway ingress controller | `azure-application-gateway` | Public internet | Public |
| NGINX Ingress Controller | `recommendation-internal-nginx` | Internal VNet | Private |

They did not conflict because every ingress resource declared its class explicitly. This pattern gave us the right tool for each traffic domain instead of forcing one controller to do everything.

### Lesson 3: Keep the Data Layer Boring

We did not try to containerize Cassandra, Kafka, or Elasticsearch on day one. We moved them to Azure VMs, kept the same operational model, and let the teams focus on the application migration. That decision prevented the migration from turning into a distributed systems science project.

---

## Final Architecture

```
Internet
   │
   ▼
Azure Application Gateway
   ├── /recommend/*      → ranking-engine VMs
   ├── /feed/*           → feed-api pods
   ├── /items/*          → item-catalog pods
   ├── /users/*          → user-profile pods
   └── /events/*         → event-collector pods

AKS — recommendation-prod
   ├── NGINX Ingress Controller (internal LB, private IP)
   │     └── /search, /rank, /profile, /events
   └── 30+ microservices via Helm

Azure VMs
   ├── Cassandra cluster (3 nodes)
   ├── Kafka cluster (3 brokers)
   ├── Elasticsearch cluster (3 nodes)
   ├── Consul service discovery
   └── Ranking engine VMs (2 nodes, local NVMe index)
```

---

## Impact

The migration changed how the platform team worked:

- **Deployments went from manual config edits to one-line Helm upgrades.**
- **New services could be onboarded in minutes** instead of days of load-balancer ticket queues.
- **Internal service-to-service latency stayed in the sub-millisecond range** thanks to the internal load balancer.
- **The ranking engine stayed stable** because we did not force it into a shape it was not ready for.
- **We hit the data center exit deadline with zero customer-facing downtime.**

The architecture is not pure Kubernetes, and that is the point. A good migration respects the workloads that are ready to move and gives a stable contract to the ones that are not.

---

If you are planning a similar move, start with the data layer, build one reusable deployment pattern, and do not be afraid to leave the loud, stateful services on VMs until they are ready to move. Kubernetes will still be there when they are.
