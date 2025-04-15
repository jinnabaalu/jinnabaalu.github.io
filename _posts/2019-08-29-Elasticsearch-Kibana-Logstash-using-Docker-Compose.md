---
layout: post
title: Elasticsearch Single Node using Docker Compose
categories: [ Storage, Elasticsearch ]
description: Deploying the elasticsearch and Kibana as docker containers 
image: "assets/img/elasticsearch.svg"
---

{% include docker-prerequisites.md %}

## Deploy Elasticsearch Single node with Docker Compose
The ELK Stack (Elasticsearch, Logstash and Kibana) can be installed on a variety of different operating systems and in various different setups. 


Elasticsearch Single Node Instance and Kibana Using Docker Compose. Create the `docker-compose.yml` with the following

```yaml
version: '3'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.3.1
    container_name: elasticsearch
    environment:
      - node.name=ws-es-node
      - discovery.type=single-node
      - cluster.name=ws-es-data-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms1024m -Xmx1024m"
      # - xpack.security.enabled='false'
      # - xpack.monitoring.enabled='false'
      # - xpack.watcher.enabled='false'
      # - xpack.ml.enabled='false'
      # - http.cors.enabled='true'
      # - http.cors.allow-origin="*"
      # - http.cors.allow-methods=OPTIONS, HEAD, GET, POST, PUT, DELETE
      # - http.cors.allow-headers=X-Requested-With,X-Auth-Token,Content-Type, Content-Length
      - logger.level: debug
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - jinnabaluesdata:/usr/share/elasticsearch/data
    ports:
      - 9200:9200
    networks:
      - esnet
    
volumes:
  jinnabaluesdata:
    driver: local

networks:
  esnet:
```

## Run 

```bash
docker-compose up -d
```
