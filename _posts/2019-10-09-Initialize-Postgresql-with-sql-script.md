---
layout: blog
title:  "PostgreSQL with Init Data using Docker Compose"
description: Initialise PostgreSQL container with user, database, and seed data
categories: [ Database, PostgreSQL ]
tags: [ PostgreSQL, Docker ]
image: "assets/img/postgres/PostgresInitData.svg"
---

{% include container-prerequisites.md %}

## Deploy PostgreSQL with Init Data using Docker Compose

Create the `docker-compose.yml` with the following:

<pre> {% include postgres/init-data-compose.yml %} </pre>

Create the `init.sql` with the following content:

<pre> {% include postgres/init.sql %} </pre>

#### Run

```bash
docker-compose up -d
```

#### Verify
```bash
# Container status
docker ps -a
# Check the Data is pre initialised
docker exec -it postgres bash
psql -U vbv -d vbvdb
SELECT * FROM employees;
```

**OUTPUT**
```bash
docker ps -a                                                                            ░▒▓ 2 ✘  01:48:36 am 
CONTAINER ID  IMAGE                          COMMAND     CREATED         STATUS                   PORTS                   NAMES
52c54521505e  docker.io/library/postgres:17  postgres    20 seconds ago  Up 21 seconds (healthy)  0.0.0.0:5432->5432/tcp  postgres

~/jinnabalu.github.io/_i/postgres:/# docker exec -it postgres bash                                    ░▒▓ ✔  01:48:47 am 
root@52c54521505e:/# psql -U vbv -d vbvdb
psql (17.4 (Debian 17.4-1.pgdg120+2))
Type "help" for help.

vbvdb=> SELECT * FROM employees;
 id | name  | position  |  salary
----+-------+-----------+-----------
  1 | Bhuvi | Manager   | 675000.00
  2 | Vibhu | Developer | 555000.00
  3 | Rudra | Analyst   | 460000.00
(3 rows)
```

####  Activity log
[https://gist.github.com/jinnabaalu/89bd8eeba3b8845cf337b85a807748f1](https://gist.github.com/jinnabaalu/89bd8eeba3b8845cf337b85a807748f1)

## Conclusion
Now that we’ve had hands-on experience initializing a PostgreSQL container with data, following the above steps, you’ve provisioned a container that automatically sets up a database, user, and seed data using a simple SQL script. This setup is perfect for local development, testing environments, and CI/CD pipelines where consistent and repeatable database states are essential.