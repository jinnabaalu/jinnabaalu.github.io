---
layout: post
title: "Cassandra - Cassandra single node cluster as a container"
description: "Cassandra - Single Node using Docker Compose"
categories: [ Cassandra, Docker, NOSQL, Database ]
image: assets/img/Cassandra_single_node.png
featured: false
hidden: true
---


- How to run cassandra as a container?
- How to run cassandra as a single node cluster?

To answer the above, Docker provides a `Docker Official Images` for Apache Cassandra, is an open-source distributed storage system.

## Create the docker-compose

- Create a `docker-compose.yml` with the following

```bash
version: '3'
services:
    cassandra-one:
        image: cassandra:3.9
        # volumes:
        #     - cassandra-volume:/var/lib/cassandra/
        ports:
            - 7000:7000
            - 7001:7001
            - 7199:7199
            - 9042:9042
            - 9160:9160
        environment:
            - CASSANDRA_CLUSTER_NAME='sample-cluster'
            - CASSANDRA_NUM_TOKENS=256
            - CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch
            - CASSANDRA_DC=sample-datacenter-one
            - CASSANDRA_RPC_ADDRESS=0.0.0.0
        restart: always
# volumes:
#   cassandra-volume:
#     driver: local
#     driver_opts:
#       o: bind
#       type: none
#       device: /root/db/cassandra-volume/
    
```

[![Try in PWD](https://cdn.rawgit.com/play-with-docker/stacks/cff22438/assets/img/button.png)](http://play-with-docker.com?stack=https://raw.githubusercontent.com/JinnaBalu/cassandra/master/single-node-cluster/cassandra.yml){:target="_blank"}

- To maintain the persistency of the data uncomment the volumes in the service and respective Volume 
