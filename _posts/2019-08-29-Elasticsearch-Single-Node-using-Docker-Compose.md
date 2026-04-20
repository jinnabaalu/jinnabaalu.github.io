---
layout: blog
title: "Elasticsearch Single Node with Docker Compose"
description: "Deploy Elasticsearch single node using Docker Compose — with CRUD operations, cluster health, and API exploration"
author: jinnabalu
categories: [ NoSQL, Search Engine, Elasticsearch ]
tags: [ Elasticsearch, Docker ]
image: "assets/img/elk/ElasticsearchSingleNode.svg"
sitemap:
  lastmod: 2026-04-20
  priority: 0.8
  changefreq: monthly
---

<style>
  .term-output { background: #0d1117; border-left: 3px solid #238636; padding: 0.8rem 1rem; margin: 0.5rem 0 1rem; border-radius: 0 6px 6px 0; font-family: 'SFMono-Regular', Consolas, monospace; font-size: 0.85rem; color: #7ee787; overflow-x: auto; }
  .term-output code { color: #7ee787; background: none; padding: 0; }
  .term-note { border-left: 3px solid #9e6a03; padding: 0.8rem 1rem; border-radius: 0 6px 6px 0; margin: 1rem 0; background: #fffbeb; font-size: 0.9rem; }
  .term-table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
  .term-table th { background: #012970; color: #fff; padding: 10px 14px; text-align: left; font-size: 0.85rem; }
  .term-table td { padding: 10px 14px; border-bottom: 1px solid #dee2e6; font-size: 0.85rem; }
  .term-table td code { font-size: 0.85em; }
</style>

{% include container-prerequisites.md %}

## Deploy Elasticsearch Single Node with Docker Compose

Create the `docker-compose.yml` with the following:

```yaml
# docker-compose.yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch-wolfi:8.17.4
    container_name: elasticsearch
    environment:
      - cluster.name=oio-es-cluster
      - node.name=es-node
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - network.host=0.0.0.0
      - xpack.license.self_generated.type=trial
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms1024m -Xmx1024m"
    ports: ['9200:9200']
    volumes:
      - 'es_data:/usr/share/elasticsearch/data'
    healthcheck:
      test: curl -s http://localhost:9200 >/dev/null || exit 1
      interval: 30s
      timeout: 10s
      retries: 5
volumes:
  es_data:
```

## Run

```bash
docker-compose up -d
```

## Container Status

```bash
docker-compose ps -a
docker container ls
docker ps -a
```

## Cluster Health & Stats APIs

Once the container is up, explore the cluster:

<table class="term-table">
  <thead><tr><th>API</th><th>Command</th></tr></thead>
  <tbody>
    <tr><td>Node list</td><td><code>curl -s localhost:9200/_cat/nodes?pretty</code></td></tr>
    <tr><td>Cluster health</td><td><code>curl -s localhost:9200/_cat/health?pretty</code></td></tr>
    <tr><td>Cluster stats</td><td><code>curl -s localhost:9200/_cluster/stats?human&amp;pretty</code></td></tr>
    <tr><td>Node stats</td><td><code>curl -s localhost:9200/_nodes/stats?pretty</code></td></tr>
    <tr><td>Specific node</td><td><code>curl -s localhost:9200/_nodes/es-node/stats?pretty</code></td></tr>
    <tr><td>List indices</td><td><code>curl -s localhost:9200/_cat/indices?pretty</code></td></tr>
    <tr><td>All indices</td><td><code>curl -s localhost:9200/_cat/indices?expand_wildcards=all&amp;pretty</code></td></tr>
    <tr><td>Index-level stats</td><td><code>curl -s localhost:9200/_nodes/stats/indices?pretty</code></td></tr>
    <tr><td>Plugins</td><td><code>curl -s localhost:9200/_nodes/plugins</code></td></tr>
  </tbody>
</table>

## CRUD Operations

### Create Index

<div class="term-note">
  <strong>Without mappings:</strong> Elasticsearch auto-generates field types on the first document (dynamic mapping).<br>
  <strong>With mappings:</strong> You define field types up front for better control (e.g., <code>text</code> vs <code>keyword</code>).
</div>

```bash
curl -X PUT http://localhost:9200/ramayana_characters \
  -H "Content-Type: application/json" -d '
{
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "description": { "type": "text" }
    }
  }
}'
```

<div class="term-output"><code>{"acknowledged":true,"shards_acknowledged":true,"index":"ramayana_characters"}</code></div>

### Insert Document

```bash
curl -X POST http://localhost:9200/ramayana_characters/_doc \
  -H "Content-Type: application/json" -d '
{
  "name": "Rama",
  "description": "Hero of the Ramayana, seventh avatar of Vishnu."
}'
```

<div class="term-output"><code>{"_index":"ramayana_characters","_id":"_g1qMpYBhtVSA9-yauE0","_version":1,"result":"created", ...}</code></div>

> Copy the `_id` from the output — you'll need it for the next queries.

### Select All

```bash
curl -X GET 'http://localhost:9200/ramayana_characters/_search?pretty'
```

<div class="term-output"><code>{
  "hits": {
    "total": { "value": 1 },
    "hits": [{
      "_id": "_g1qMpYBhtVSA9-yauE0",
      "_source": {
        "name": "Rama",
        "description": "Hero of the Ramayana, seventh avatar of Vishnu."
      }
    }]
  }
}</code></div>

### Select by ID

```bash
export DOC_ID=_g1qMpYBhtVSA9-yauE0
curl -X GET "http://localhost:9200/ramayana_characters/_doc/${DOC_ID}?pretty"
```

### Update Document

```bash
curl -X POST "http://localhost:9200/ramayana_characters/_update/${DOC_ID}?pretty" \
  -H "Content-Type: application/json" -d '
{
  "doc": {
    "name": "Raama"
  }
}'
```

<div class="term-output"><code>{"_index":"ramayana_characters","_id":"...","_version":2,"result":"updated"}</code></div>

Try the GET call again to see the updated value.

### Delete Document

```bash
curl -X DELETE "http://localhost:9200/ramayana_characters/_doc/${DOC_ID}?pretty"
```

<div class="term-output"><code>{"_index":"ramayana_characters","_id":"...","_version":3,"result":"deleted"}</code></div>

## Homework

<table class="term-table">
  <thead><tr><th>#</th><th>Task</th><th>Goal</th></tr></thead>
  <tbody>
    <tr><td>1</td><td>Deploy &amp; Explore</td><td>Run Docker Compose, use <code>curl</code> to hit every health API</td></tr>
    <tr><td>2</td><td>Create &amp; Query</td><td>Create an index, insert 5 documents, run <code>_search</code> and get-by-ID</td></tr>
    <tr><td>3</td><td>Understand Mappings</td><td>Compare behaviour with and without explicit mappings</td></tr>
    <tr><td>4</td><td>Yellow Cluster?</td><td>Investigate why health turns yellow after creating an index (<em>hint: replica shards</em>)</td></tr>
  </tbody>
</table>

## Conclusion

With this setup, you can quickly spin up a single-node Elasticsearch stack for development or learning purposes, and start exploring powerful search and analytics capabilities using RESTful APIs.