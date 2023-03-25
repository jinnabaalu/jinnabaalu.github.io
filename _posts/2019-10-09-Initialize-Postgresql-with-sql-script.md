---
layout: post
title:  "Initialise Postgresql Container with init SQL script"
metadate: "hide"
categories: [ Database, PostgreSQL, SQL ]
tags: [ PostgreSQL ]
image: "assets/img/postgresql.svg"
related_posts: 
      - title: "Initialise Postgresql Container with docker-compose"
        url: "https://platform-ops.tech/Run-Postgres-Container/"
      - title: "Initialise Postgresql Container with init SQL script"
        url: "https://platform-ops.tech/Initialize-Postgresql-with-sql-script/"
      - title: "Basic command to run with Postgress Container"
        url: "https://platform-ops.tech/Basic-Commands-in-postgress-container/"
---

## Prerequisite

1. Install [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
2. install [docker-compose](https://docs.docker.com/compose/install/)

## Init SQL script with postgresql container

![](/assets/img/postgresql.svg)

- Create a `docker-compose.yml` with the following

```yml
---
version: '3.6'
services:
  postgresql:
    image: postgres:11.3
    container_name: postgres
    volumes:
      # Uncomment below to maintain the peristant data
      # - platops-data:/var/lib/postgresql/data/
      # Uncomment bellow to intialize the container with data by creating the respective file
      # - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      - POSTGRES_USER=postgress
      - POSTGRES_PASSWORD=postgress
    ports: ['5432:5432']
    networks: ['stack']
    healthcheck:
      test: curl -s https://localhost:5432 >/dev/null; if [[ $$? == 52 ]]; then echo 0; else echo 1; fi
      interval: 30s
      timeout: 10s
      retries: 5
  adminer:
    image: adminer
    restart: always
    ports:
      - 8080:8080

volumes:
  platops-data:
networks:
  stack:

```

[![Try in PWD](https://cdn.rawgit.com/play-with-docker/stacks/cff22438/assets/img/button.png)](http://play-with-docker.com?stack=https://raw.githubusercontent.com/JinnaBalu/postgreSQL/master/postgres-with-init-user-and-db.yml)

- Created a `init.sql` with the following

```sql
CREATE USER platops WITH PASSWORD 'platops';
CREATE DATABASE platopsdb;
GRANT ALL PRIVILEGES ON DATABASE platopsdb TO platops;
```

- RUN container with `docker-compose up -d`, this will start your container with initializing the database with the above scripts.

### See that it's working

```bash
docker logs -f postgres

# OR

docker logs postgres
```
