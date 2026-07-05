---
layout: post
title: "Initialise Postgresql Container with init SQL script"
date: 2024-05-28 02:42:53 +0000
metadate: "hide"
categories: [Database, PostgreSQL]
tags: [PostgreSQL]
description: "Initialize a PostgreSQL container with an init SQL script using Docker Compose."
image: "assets/img/postgresql.svg"
---

## Prerequisite

1. Install [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
2. Install [docker-compose](https://docs.docker.com/compose/install/)

## Init SQL script with postgresql container

![PostgreSQL]({{ site.baseurl }}/assets/img/postgresql.svg)

- Create a `docker-compose.yml` with the following

```yml
---
version: '3'
services:
  postgresql:
    image: postgres:12.3
    container_name: postgres
    volumes:
      # Uncomment below to maintain the persistent data
      - ct-data:/var/lib/postgresql/data/
      # Uncomment bellow to initialize the container with data by creating the respective file
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
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
    container_name: adminer
    restart: always
    ports: ['8080:8080']

volumes:
  ct-data:
networks:
  stack:
```

[![Try in PWD](https://cdn.rawgit.com/play-with-docker/stacks/cff22438/assets/images/button.png)](http://play-with-docker.com?stack=https://raw.githubusercontent.com/VibhuviOiO/infinite-containers/main/postgres/postgres-with-init-user-and-db.yml)

- Create an `init.sql` with the following

```sql
CREATE USER postgress WITH PASSWORD 'postgress';
CREATE DATABASE pdata;
GRANT ALL PRIVILEGES ON DATABASE pdata TO ct;

CREATE SEQUENCE IF NOT EXISTS recipient_seq
    START WITH 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE IF NOT EXISTS recipient
(
    id                      BIGINT                   NOT NULL,
    recipient_id            VARCHAR(255)             NOT NULL,
    first_name              VARCHAR(255)             NOT NULL,
    middle_name             VARCHAR(255)             NOT NULL,
    last_name               VARCHAR(255)             NOT NULL,
    CONSTRAINT recipient_pk PRIMARY KEY (id)
);
```

- Run the container with `docker-compose up -d`. This starts PostgreSQL and initializes the database with the above scripts.

### See that it's working

```bash
docker logs -f postgres

# OR

docker logs postgres
```
