---
layout: post
title: Elasticsearch + Kibana using Docker Compose
categories: [ Storage, Elasticsearch ]
description: Deploying the elasticsearch and Kibana as docker containers 
image: "assets/img/elasticsearch.svg"
---

{% include docker-prerequisites.md %}

## Deploy Elasticsearch + Kibana with Docker Compose

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
      - 9300:9300
    networks:
      - esnet
  kibana:
    image: docker.elastic.co/kibana/kibana:7.3.1
    container_name: kibana
    environment:
      SERVER_NAME: 127.0.0.1
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
      # XPACK_GRAPH_ENABLED: false
      # XPACK_ML_ENABLED: false
      # XPACK_REPORTING_ENABLED: false
      # XPACK_SECURITY_ENABLED: false
      # XPACK_WATCHER_ENABLED: false
    ports:
      - "5601:5601"
    networks:
      - esnet
    depends_on:
      - elasticsearch
    restart: "unless-stopped"
    
volumes:
  jinnabaluesdata:
    driver: local

networks:
  esnet:
```

### Execute docker-compose up -d in the terminal

  - Elasticsearch is available at http://localhost:8100/  

  - Kibana UI is up at http://localhost:5601/
