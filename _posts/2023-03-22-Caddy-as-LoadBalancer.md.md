---
layout: post
categories: [ Caddy, LoadBalancer ]
---



- How to run apache nifi as a container?
- How to run apache nifi as a single node cluster?

To answer the above, Docker provides a `Docker Official Images` for Apache Cassandra, is an open-source distributed storage system.

## Create the docker-compose

- Create a `docker-compose.yml` with the following

{% raw %}{% include https://raw.githubusercontent.com/JinnaBalu/docker-caddy/main/reverse-proxy/docker-compose.yml %}{% endraw %}

```bash

version: "3"
services:
  zookeeper:
    hostname: zookeeper
    container_name: zookeeper
    image: 'bitnami/zookeeper:latest'
    environment:
      - ALLOW_ANONYMOUS_LOGIN=yes
  nifi:
    image: apache/nifi:1.12.1
    ports:
      - 8080
    environment:
      - NIFI_WEB_HTTP_PORT=8080
      - NIFI_CLUSTER_IS_NODE=true
      - NIFI_CLUSTER_NODE_PROTOCOL_PORT=8082
      - NIFI_ZK_CONNECT_STRING=zookeeper:2181
      - NIFI_ELECTION_MAX_WAIT=1 min
    
```

[![Try in PWD](https://cdn.rawgit.com/play-with-docker/stacks/cff22438/assets/img/button.png)](http://play-with-docker.com?stack=https://raw.githubusercontent.com/JinnaBalu/infinite-stack/master/nifi/docker-compose.yml){:target="_blank"}
