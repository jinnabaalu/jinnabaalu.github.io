---
layout: blog
title:  "Elasticsearch Secure Cluster with TLS using Docker Compose"
description: Securing Elasticsearch with TLS, Kibana, and API access via Docker Compose.
metadata: "hide"
categories: [ NoSQL, Search Engine, Elasticsearch, TLS ]
tags: [ Elasticsearch, Security, TLS, Kibana ]
image: "assets/img/elk/SecureElasticsearchKibana.svg"
---

{% include container-prerequisites.md %}

## Securing Elasticsearch Cluster with TLS and Kibana UI

Let us understand how we can secure the elasticsearch, and integrate Kibana and accessing it via both curl and Kibana UI.

#### Generate the TLS files
The TLS certificates will help secure the cluster to support features like encryption, authentication and access control.

- Create `instances.yml`
```yaml
instances:
  - name: es-node
    dns:
      - es-node
    ip:
      - 127.0.0.1
  - name: kibana
    dns:
      - kibana
    ip:
      - 127.0.0.1
```
- Generate certs using elasticsearch-certutil
```bash
docker run --rm -v $(pwd):/certs -w /certs docker.elastic.co/elasticsearch/elasticsearch:8.12.2 elasticsearch-certutil cert --silent --in instances.yml --out certs.zip --pem

unzip certs.zip -d certs
```
#### Docker Compose with TLS & Kibana


```bash
docker-compose up -d
docker ps -a
```

#### Access Secured Elasticsearch API via curl
```bash
curl --cacert certs/ca/ca.crt -u elastic:password https://localhost:9200/_cluster/health?pretty
curl --cacert certs/ca/ca.crt -u elastic:password https://localhost:9200/_cat/nodes?v
```

#### Login to Kibana and try above APIs
- Open https://localhost:5601
- Accept the certificate warning in browser
- Login with elastic user and password
- Navigate to Dev Tools in Kibana sidebar to Mirror curl Queries
```bash
GET _cat/nodes?v
GET _cluster/health
GET ramayana_characters/_search
```

##### Explore Kibana Features
- Index Management: View and manage indices
- Stack Management: Users, roles, certificates
- Visualizations: Create charts with Lens
- Dashboards: Combine visualizations for insights
- Observability: Logs, metrics (if configured)

## Homework

#### Deploy & Explore
Run the Docker Compose setup and use curl commands to explore APIs (nodes, health, indices). This builds confidence.

#### Create & Query
Create a simple index, insert documents, and run basic queries (_search, get by ID). Understand JSON structure.

#### Understand Mappings
Compare behavior with and without mappings to grasp how Elasticsearch treats data.

#### Check the Cluster Health, it turns yellow

Investigate the reason behind the yellow status of a cluster after creating the first index. Understand the concept of primary shards and replica shards.

## Conclusion

This setup introduces real-world security practices for Elasticsearch with TLS and Kibana UI, giving you hands-on exposure to protected API access and observability tools.