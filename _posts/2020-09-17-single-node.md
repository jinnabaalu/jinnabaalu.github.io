---
layout: post
title: "Elasticsearch - Single Node using Docker Compose"
description: "Elasticsearch - Single Node using Docker Compose"
author: jinnabalu
categories: [ Elasticsearch, Docker, Database ]
image: assets/img/Elasticsearch_main.png
featured: false
hidden: true
---

## Preface

This post assumes that you have some basic understanding of Docker, Docker Compose, and the key components used in the docker ecosystem. Get up to speed, with the [Prepare Your Docker Eenvironment](https://docs.docker.com/get-started/#prepare-your-docker-environment) section of Docker docs.

1. Install [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
2. install [docker-compose](https://docs.docker.com/compose/install/)

## Deploy Elasticsearch Single Node

The ELK Stack (Elasticsearch, Logstash, and Kibana) can be installed on a variety of different operating systems and in various setups. The most easiest way to deploy elastic search as a container, we have Responsive deployment and scaling, Running more workloads on the same hardware which will hep developer and production environments with more flexibility.  

Elasticsearch Single Node container using Docker Compose. Create the `docker-compose.yml` with the following

```yaml
version: '3.7'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.7.0
    container_name: elasticsearch
    environment:
      - node.name=jinnabalu-node
      - discovery.type=single-node
      - cluster.name=jinnabalu-es-data-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms1024m -Xmx1024m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - jinnabaluesdata:/usr/share/elasticsearch/data
    ports:
      - 9200:9200
    networks:
      - elastic
networks:
  elastic:
    driver: bridge  
volumes:
  jinnabaluesdata:
```

## Run 

```bash
docker-compose up -d
```
### Deploy Elasticsearch Single Node with Kibana

Elasticsearch Single Node container with Kibana Using Docker Compose. Create the `docker-compose.yml` with the following

```yaml
https://raw.githubusercontent.com/JinnaBalu/jinnabalu-infinite-containers/master/elasticsearch/single-node.yml
```

```yaml
version: '3.7'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.7.0
    environment:
      - node.name=jinnabalu-node
      - discovery.type=single-node
      - cluster.name=jinnabalu-es-data-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms1024m -Xmx1024m"
    volumes:
      - jinnabaluesdata:/usr/share/elasticsearch/data
    ports:
      - 9200:9200
    networks:
      - elastic
    deploy:
      replicas: 1
      update_config:
        parallelism: 1
        delay: 180s
      restart_policy:
        condition: on-failure      
  kibana:
    image: docker.elastic.co/kibana/kibana:7.7.0
    ports:
      - 5601:5601
    environment:
      ELASTICSEARCH_URL: http://elasticsearch:9200
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    networks:
      - elastic
    deploy:
      replicas: 1
      update_config:
        parallelism: 1
        delay: 180s
      restart_policy:
        condition: on-failure    
      placement:
        constraints: [node.role == manager]
networks:
  elastic:
volumes:
  jinnabaluesdata:
```

## Run 

```bash
docker-compose up -d
```

