---
layout: post
title: "Elasticsearch Disk Space is too low"
description: "Elasticsearch - [FORBIDDEN/12/index read-only / allow delete (api)];];"
author: jinnabalu
categories: [ ElasticsearchIssues, Database ]
image: assets/img/Elasticsearch_watermark.png
---

*Fix the FORBIDDEN Read-Only / Allow Delete Error for Elasticsearch API Requests*

Elasticsearch considers the available disk space on a node before deciding whether to allocate new shards to that node or to actively relocate shards away from that node.

Elasticsearch reads the disk space, makes all the indices into *READ ONLY* when the "Cluster Settings" are default and reaches the watermark levels. We can disable this by updating the ` disk allocation decider` as follows

```bash
curl -X PUT "localhost:9200/twitter/_settings?pretty" -H 'Content-Type: application/json' -d'
{
  cluster.routing.allocation.disk.threshold_enabled": false
}
'
```

We can customize the watermark level default values to the required, here is the default values

- `cluster.routing.allocation.disk.watermark.low: (Default 85%)`
- `cluster.routing.allocation.disk.watermark.high: (Default 90%)` 
- `cluster.routing.allocation.disk.watermark.flood_stage: (Default 95%)`

To know more about the disk allocation [read here](https://www.elastic.co/guide/en/elasticsearch/reference/6.8/disk-allocator.html)

### Priority #1

In Production Elasticsearch Cluster deleting duplicates data or updating any of the above defaults is bad practice as we are in hurry to resolve the issue on fly. Deleting any data decision takes ample amount of time. Take an action of increasing the disk space before cluster goes into *READ ONLY* node. Temporarily update `threshold_enabled` value to false and increase the disk space.

> For monitoring or staging servers we can go for the below priorities. Don't read Priority #2 and Priority #3, if you are doing it on production server, we make mistakes, deleting any production index cost more, be conscious doing any of the deleting activities.

Recommended only for staging/pre-production/monitoring/

### Priority #2

Delete the unwanted indices or unwanted data from the disk

### Priority #3

Update the `cluster.routing.allocation.disk.` default values to set them according to the requirement, this is recommended on dev machine. By setting the `cluster.routing.allocation.disk.watermark` levels we can re-enable the index to writable.

Watermark levels can be set in two ways, but we can't mix both

- Absolute byte values 
- Percentage values

#### Absolute Bytes

```bash
curl -X PUT "localhost:9200/_cluster/settings?pretty" -H 'Content-Type: application/json' -d'
{
  "transient": {
    "cluster.routing.allocation.disk.watermark.low": "5gb",
    "cluster.routing.allocation.disk.watermark.high": "3gb",
    "cluster.routing.allocation.disk.watermark.flood_stage": "1gb"
  }
}
'

# Here the above example works for indexing smaller number of documents/sec in dev or test

```
#### Percentage values

```bash
curl -X PUT "localhost:9200/_cluster/settings?pretty" -H 'Content-Type: application/json' -d'
{
  "transient": {
    "cluster.routing.allocation.disk.watermark.low": "90%",
    "cluster.routing.allocation.disk.watermark.high": "95%",
    "cluster.routing.allocation.disk.watermark.flood_stage": "98%"
  }
}
'
```

> Note: Enable the `cluster.routing.allocation.disk.threshold_enabled: true`, when the cluster is stable and health is green, so the warnings will be thrown based on the disk usage. Disabling leads to stop the elasticsearch cluster.