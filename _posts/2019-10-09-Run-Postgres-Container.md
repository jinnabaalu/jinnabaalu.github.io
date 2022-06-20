---
layout: post
title:  "Initialise Postgresql Container with docker-compose"
metadate: "hide"
categories: [ Database, PostgreSQL ]
tags: [ PostgreSQL ]
image: "assets/images/postgresql.svg"
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

- Create a `docker-compose.yml` with the following

```yml
---
version: '3'
services:
  postgress-postgresql:
    image: postgres:11.4
    container_name: postgres
    volumes:
        - data-postgresql:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=postgress
      - POSTGRES_PASSWORD=
    ports: ['5432:5432']

volumes:
  data-postgresql:
```

- Set the custom volume for the postgres persistency, update the docker volume of the above yml with the following

```yml
...
...
..

volumes:
  data-postgresql:
    driver: local
    driver_opts:
      o: bind
      type: none
      device: /path/of/db/postgres/data/  
```

- Run

```bash
docker-compose up -d
```
### Check with the logs 

```bash
docker logs postgres
```


