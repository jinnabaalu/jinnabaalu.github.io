---
layout: post
title:  "MongoDB Single Node Cluster with Replicaset"
categories: [ MongoDB, NoSQL ]
image: assets/img/mongodb/1.png
featured: false
hidden: true
githublink: https://github.com/jinnabaalu/infinite-containers/tree/main/mongo/single-node-rs
docker: true
---

{% include docker-prerequisites.md %}

{% include create-mongodb-keyfile.md %}

### Create the docker-compose 

- Create the `docker-compose.yml` in `single-node-rs` directory

    `$ cd docker-mongo && mkdir single-node-rs && touch docker-compose.yml`

- Copy the following content and save in `docker-compose.yml`

    ```yaml
    version: "3.9"
    services:
      mongodb:
        image : mongo:6
        container_name: mongodb
        hostname: mongodb
        restart: on-failure
        environment:
          - PUID=1000
          - PGID=1000
          - MONGO_INITDB_ROOT_USERNAME=mongouser
          - MONGO_INITDB_ROOT_PASSWORD=mongopass
          - MONGO_INITDB_DATABASE=mydatabase
          - MONGO_REPLICA_SET_NAME=devrs
          - TZ="UTC"
        volumes:
          - mongodb_data:/data/db
          # Use below line if you are running the container in linux machine
          # - ../keyfile-linux/mongoKeyFileLinux:/opt/keyfile/mongoKeyFileLinux
          # Use below line if you are running the container in linux machine
          - ../keyfile-mac/mongoKeyFileMac:/opt/keyfile/mongoKeyFileMac
        ports:
          - 27017:27017
        healthcheck:
          test: |
            test $$(mongosh --quiet -u mongouser -p mongopass --eval "try { rs.initiate({ _id: 'devrs', members: [{ _id: 0, host: 'mongodb' }] }).ok } catch (_) { rs.status().ok }") -eq 1
          interval: 10s
          start_period: 30s
        command: ["mongod", "--replSet", "devrs", "--bind_ip", "localhost,mongodb",  "--keyFile", "/opt/keyfile/mongoKeyFileMac"]
        #command: "--bind_ip_all --keyFile /opt/keyfile/keyfile --replSet devrs"
    volumes:
      mongodb_data:
    ```
### Run the Application

- Run the application

    `$ cd docker-mongo/single-node-rs/`
    `docker-compose up -d`

- Check the status whether the docker service is up or down `$ docker ps -a`

- Check the logs 
    `$ docker logs mongodb`


#### Reference

- [Create keyfile]()
- [Deploy Replica Set With Keyfile Authentication](https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-with-keyfile-access-control/#deploy-replica-set-with-keyfile-authentication)
- [Internal/Membership Authentication](https://www.mongodb.com/docs/manual/core/security-internal-authentication/)