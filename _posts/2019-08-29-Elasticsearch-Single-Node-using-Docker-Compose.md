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

<pre> {% include elk/single-node-compose.yml %} <pre>

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

curl -XGET 'localhost:9200/_nodes/es-node/stats?pretty'

# GET Indices, initally there are no custom indices

curl -XGET 'localhost:9200/_cat/indices?pretty'

# GET ALL Indices

curl -XGET 'localhost:9200/_cat/indices?expand_wildcards=all&pretty'

# Index Level Stats, It includes the stats about the default indices as well. 

curl -XGET 'localhost:9200/_nodes/stats/indices?pretty'

# Retrieve data on plugins or ingest:

curl -XGET 'localhost:9200/_nodes/plugins'
```

#### CRUD Operation

##### Create Index
>**Without mappings:** Elasticsearch auto-generates field types when you index the first document (dynamic mapping).

> **With mappings:** You define field types up front for better control (e.g., setting text vs keyword).

```bash
curl -X PUT http://localhost:9200/ramayana_characters -H "Content-Type: application/json" -d '
{
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "description": { "type": "text" }
    }
  }
}'
```


**OUTPUT**
```bash
{"acknowledged":true,"shards_acknowledged":true,"index":"ramayana_characters"}
```

##### Insert Document

```bash
curl -X POST http://localhost:9200/ramayana_characters/_doc -H "Content-Type: application/json" -d '
{
  "name": "Rama",
  "description": "Hero of the Ramayana, seventh avatar of Vishnu."
}'
```

**OUTPUT**
```bash
{"_index":"ramayana_characters","_id":"_g1qMpYBhtVSA9-yauE0","_version":1,"result":"created","_shards":{"total":2,"successful":1,"failed":0},"_seq_no":0,"_primary_term":1}
```

> COPY ID FROM ABOVE OUTPUT `"_id":"_g1qMpYBhtVSA9-yauE0"` FOR NEXT QUERIES

##### Select All

```bash
curl -X GET 'http://localhost:9200/ramayana_characters/_search?pretty'
```

**OUTPUT**
```bash
{
  "took" : 154,
  "timed_out" : false,
  "_shards" : {
    "total" : 1,
    "successful" : 1,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 1,
      "relation" : "eq"
    },
    "max_score" : 1.0,
    "hits" : [
      {
        "_index" : "ramayana_characters",
        "_id" : "_g1qMpYBhtVSA9-yauE0",
        "_score" : 1.0,
        "_source" : {
          "name" : "Rama",
          "description" : "Hero of the Ramayana, seventh avatar of Vishnu."
        }
      }
    ]
  }
}
```

##### Select by ID
> Replace the ID from the previous OUTPUTS


```bash
export DOC_ID=_g1qMpYBhtVSA9-yauE0;
curl -X GET "http://localhost:9200/ramayana_characters/_doc/${DOC_ID}?pretty"
```

**OUTPUT**
```bash
{
  "_index" : "ramayana_characters",
  "_id" : "_g1qMpYBhtVSA9-yauE0",
  "_version" : 2,
  "_seq_no" : 1,
  "_primary_term" : 1,
  "found" : true,
  "_source" : {
    "name" : "Raama",
    "description" : "Hero of the Ramayana, seventh avatar of Vishnu."
  }
}
```

##### Update Document
```bash
curl -X POST "http://localhost:9200/ramayana_characters/_update/${DOC_ID}?pretty" -H "Content-Type: application/json" -d '
{
  "doc": {
    "name": "Raama"
  }
}'
```

**OUTPUT**
```bash
{
  "_index" : "ramayana_characters",
  "_id" : "_g1qMpYBhtVSA9-yauE0",
  "_version" : 2,
  "result" : "noop",
  "_shards" : {
    "total" : 0,
    "successful" : 0,
    "failed" : 0
  },
  "_seq_no" : 1,
  "_primary_term" : 1
}
```

Try GET call again and see the updated value. 

##### Delete Document

```bash
curl -X DELETE "http://localhost:9200/ramayana_characters/_doc/${DOC_ID}?pretty"
```

**OUTPUT**
```bash
{
  "_index" : "ramayana_characters",
  "_id" : "_g1qMpYBhtVSA9-yauE0",
  "_version" : 3,
  "result" : "deleted",
  "_shards" : {
    "total" : 2,
    "successful" : 1,
    "failed" : 0
  },
  "_seq_no" : 2,
  "_primary_term" : 1
}
```

## Homework

#### Deploy & Explore
Run the Docker Compose setup and use curl commands to explore APIs (nodes, health, indices). This builds confidence.

#### Create & Query
Create a simple index, insert documents, and run basic queries (_search, get by ID). Understand JSON structure.

#### Understand Mappings
Compare behavior with and without mappings to grasp how Elasticsearch treats data.

## Conclusion

With this setup, you can quickly spin up a single-node Elasticsearch and Kibana stack for development or learning purposes, and start exploring powerful search and analytics capabilities using RESTful APIs.