---
layout: post
title:  "MongoDB Three Node Cluster with Replicaset in a Single Server for POC"
categories: [ MongoDB, NoSQL ]
image: assets/img/mongodb/1.png
featured: false
hidden: true
githublink: https://github.com/JinnaBalu/docker-mongo
githubreponame: docker-mongo
docker: true
---

{% include docker-prerequisites.md %}

{% include create-mongodb-keyfile.md %}

### Create the docker-compose 

- Create the `docker-compose.yml` in `three-node-rs` directory

    `$ cd docker-mongo && mkdir three-node-rs && touch docker-compose.yml`

- Copy the following content and save in `docker-compose.yml`

    ```yaml
    version: '3.9'
    services:
      mongo1:
        image: mongo:6
        container_name: mongo1
        restart: unless-stopped
        environment:
          - PUID=1000
          - PGID=1000
          - MONGO_INITDB_ROOT_USERNAME=mongouser
          - MONGO_INITDB_ROOT_PASSWORD=mongopass
          - MONGO_INITDB_DATABASE=mydatabase
          - MONGO_REPLICA_SET_NAME=devrs
          - TZ="UTC"
        volumes:
          - mongo1-data:/data/db
          # Use below line if you are running the container in linux machine
          # - ../keyfile-linux/mongoKeyFileLinux:/opt/keyfile/mongoKeyFileLinux
          # Use below line if you are running the container in linux machine
          - ../keyfile-mac/mongoKeyFileMac:/opt/keyfile/mongoKeyFileMac
        ports:
          - "27017:27017"
        healthcheck:
          test: |
            test $$(mongosh --quiet -u mongouser -p mongopass --eval "rs.status().ok") -eq 1
          interval: 10s
          start_period: 30s
        command: ["mongod", "--replSet", "devrs", "--bind_ip", "localhost,mongo1", "--auth",  "--keyFile", "/opt/keyfile/mongoKeyFileMac"]
        networks:
          mongoCluster:
        
      mongo2:
        image: mongo:6
        container_name: mongo2
        restart: unless-stopped
        environment:
          - PUID=1000
          - PGID=1000
          - MONGO_INITDB_ROOT_USERNAME=mongouser
          - MONGO_INITDB_ROOT_PASSWORD=mongopass
          - MONGO_INITDB_DATABASE=mydatabase
          - MONGO_REPLICA_SET_NAME=devrs
          - TZ="UTC"
        volumes:
          - mongo2-data:/data/db
          - ../keyfile-mac/mongoKeyFileMac:/opt/keyfile/mongoKeyFileMac
        healthcheck:
          test: |
            test $$(mongosh --quiet -u mongouser -p mongopass --eval "rs.status().ok") -eq 1
          interval: 10s
          start_period: 30s
        networks:
          mongoCluster:
        command: ["mongod", "--replSet", "devrs", "--bind_ip", "localhost,mongo2", "--auth",  "--keyFile", "/opt/keyfile/mongoKeyFileMac"]

      mongo3:
        image: mongo:6
        container_name: mongo3
        restart: unless-stopped
        environment:
          - PUID=1000
          - PGID=1000
          - MONGO_INITDB_ROOT_USERNAME=mongouser
          - MONGO_INITDB_ROOT_PASSWORD=mongopass
          - MONGO_INITDB_DATABASE=mydatabase
          - MONGO_REPLICA_SET_NAME=devrs
          - TZ="UTC"
        volumes:
          - mongo3-data:/data/db
          - ../keyfile-mac/mongoKeyFileMac:/opt/keyfile/mongoKeyFileMac
        healthcheck:
          test: |
            test $$(mongosh --quiet -u mongouser -p mongopass --eval "rs.status().ok") -eq 1
          interval: 10s
          start_period: 30s
        networks:
          mongoCluster:
        command: ["mongod", "--replSet", "devrs", "--bind_ip", "localhost,mongo3", "--auth",  "--keyFile", "/opt/keyfile/mongoKeyFileMac"]
      mongo-express:
        image: mongo-express
        container_name: mongo-express
        restart: always
        ports:
          - 127.0.0.1:8081:8081
        networks:
          mongoCluster:
        environment:
          ME_CONFIG_MONGODB_SERVER: mongo1
          ME_CONFIG_BASICAUTH_USERNAME: admin
          ME_CONFIG_BASICAUTH_PASSWORD: admin123
          # ME_CONFIG_MONGODB_AUTH_DATABASE: admin
          ME_CONFIG_MONGODB_ADMINUSERNAME: mongouser
          ME_CONFIG_MONGODB_ADMINPASSWORD: mongopass
          ME_CONFIG_MONGODB_URL: mongodb://mongouser:mongopass@mongo1:27017/
    networks:
      mongoCluster:
    volumes:
      mongo1-data:
      mongo2-data:
      mongo3-data:

    ```
### Run the Application

- Run the application

    `$ cd docker-mongo/three-node-rs/`
    `docker-compose up -d`

### Initialise the Cluster 

```bash
docker exec -it mongo1 mongosh --quiet -u mongouser -p mongopass --eval "rs.initiate({
 _id: \"devrs\",
 members: [
   {_id: 0, host: \"mongo1\"},
   {_id: 1, host: \"mongo2\"},
   {_id: 2, host: \"mongo3\"}
 ]
})"
```

Expected Output is 

```bash
{ ok: 1 }
```


- Check the status whether the docker service is up or down `$ docker ps -a`

- Check the logs 
    `$ docker logs mongodb`


#### Reference

- [Create keyfile]()
- [Deploy Replica Set With Keyfile Authentication](https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-with-keyfile-access-control/#deploy-replica-set-with-keyfile-authentication)
- [Internal/Membership Authentication](https://www.mongodb.com/docs/manual/core/security-internal-authentication/)