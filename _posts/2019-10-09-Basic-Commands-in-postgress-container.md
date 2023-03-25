---
layout: post
title:  "Basic command to run with Postgress Container"
metadate: "hide"
categories: [ Database, PostgreSQL, SQL ]
description: "Import or export postgress db, how to run the psql commands, Create a database with postgres container"
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


### Connect to the database itself

If we want to intect with our database we need to interact with postgres database first

```bash
docker exec -it postgres psql -Upostgress
```
### Create user and database with all privileges entering the container

```bash
docker exec -it postgres bash

psql -Upostgress

CREATE USER platops WITH PASSWORD 'platops';
CREATE DATABASE platopsdb;
GRANT ALL PRIVILEGES ON DATABASE platopsdb TO platops;
```

### Run psql commands without entering the container

- To run `psql`

```bash
docker exec -it postgres psql -U platops
```

- Create a database

```bash
docker exec -it postgres psql -U platops -c "create database platops"
```

- Run Select Query

```bash
docker exec -it postgres psql -Upostgres -a platops -c 'SELECT * FROM posts;'
```

### Import or Export with psql CLI


- Backup Database

```bash
docker exec -t postgres pg_dumpall -c -U platops > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
```

- Restore Databases

```bash
cat dump.sql | docker exec -i postgres psql -U postgres
```

