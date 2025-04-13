---
layout: blog
title:  "Elasticsearch Single Node using Docker Compose"
description: Deploying the elasticsearch as docker containers 
metadata: "hide"
categories: [ NoSQL, Search Engine, Elasticsearch ]
tags: [ Elasticsearch ]
image: "assets/img/elk/ElasticsearchSingleNode.svg"
---

{% include container-prerequisites.md %}

## Deploy Elasticsearch Single node with docker-compose

Elasticsearch Single Node Instance Using Docker Compose. 

Create the `docker-compose.yml` with the following

<pre> {% include elk/single-node-compose.yml %} </pre>

#### Run 

```bash
docker-compose up -d
```

#### Container Status

```bash
docker-compose ps -a

docker container ls 

docker ps -a
```

#### Check the APIs
```bash
# Get nodes
curl -XGET 'localhost:9200/_cat/nodes?pretty'

# Get health
curl -XGET 'localhost:9200/_cat/health?pretty'

# Cluster stats
curl -XGET 'localhost:9200/_cluster/stats?human&pretty'

# Node Stats
curl -XGET 'localhost:9200/_nodes/stats?pretty'

# A specific node stats:

curl -XGET 'localhost:9200/_nodes/node-1/stats?pretty'

# Index Level Stats:

curl -XGET 'localhost:9200/_nodes/stats/indices?pretty'

# Retrieve data on plugins or ingest:

curl -XGET 'localhost:9200/_nodes/plugins'
```

#### CRUD Operation

##### Create Index
```bash
curl -X PUT http://localhost:9200/ramayana_characters -H "Content-Type: application/json" -d '
{
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "name": { "type": "text" },
      "description": { "type": "text" }
    }
  }
}'
```

##### Insert Document

```bash
curl -X POST http://localhost:9200/ramayana_characters/_doc -H "Content-Type: application/json" -d '
{
  "id": "uuid-1",
  "name": "Rama",
  "description": "Hero of the Ramayana, seventh avatar of Vishnu."
}'
```

##### Select All

```bash
curl -X GET http://localhost:9200/ramayana_characters/_search?pretty
```

##### Select by ID
```bash
curl -X GET http://localhost:9200/ramayana_characters/_doc/[UUID]
```

##### Update Document
```bash
curl -X POST http://localhost:9200/ramayana_characters/_update/[UUID] -H "Content-Type: application/json" -d '
{
  "doc": {
    "name": "Raama"
  }
}'
```

##### Delete Document

```bash
curl -X DELETE http://localhost:9200/ramayana_characters/_doc/[UUID]
```

## Conclusion

With this setup, you can quickly spin up a single-node Elasticsearch and Kibana stack for development or learning purposes, and start exploring powerful search and analytics capabilities using RESTful APIs.